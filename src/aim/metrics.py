import json
from pathlib import Path
from typing import Dict, List, Optional, Union
from .claim_checking.claim_checker import ClaimChecker
from .claim_checking.mcp_checker import MCPChecker
from .claim_checking.vector_checker import RetrieverChecker
from .models.embeddings.embeddings_service import EmbeddingService
from .models.llm.llm_service import LLMService
from .claim_checking.web_checker import WebChecker
from .data_sources import DataSource
from sklearn.metrics.pairwise import cosine_similarity
from .state import ExecutionMode, ExecutionModes, get_mode
import numpy as np

class Metrics:
    def __init__(
        self,
        reference_id: str,
        llm_model: Optional[str],
        llm_api_key: Optional[str],
        embed_api_key: Optional[str], 
        embed_model: Optional[str],
        claim_check_threshold: Optional[float] = None,
        criteria_check_threshold: Optional[float] = None,
        similarity_threshold: Optional[float] = None,
    ):
        self.reference_id = reference_id
        self.llm_service = LLMService(llm_api_key, llm_model)
        self.embeds_service = EmbeddingService(embed_api_key, embed_model)
        self.claim_check_threshold = claim_check_threshold
        self.criteria_check_threshold = criteria_check_threshold
        self.similarity_threshold = similarity_threshold

    def _load_json(self, path: Path, default):
        if not path.exists():
            return default
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _save_json(self, path: Path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def similarity_score(self, candidate: str, assertion_id: str, threshold: Optional[float] = None):
        handler = self._handler(get_mode(), threshold)
        return handler(candidate, assertion_id)

    def _handler(self, mode, threshold=None):
        return {
            ExecutionModes.ASSERT: lambda candidate, assertion_id: self._assert_similarity(candidate, assertion_id, threshold),
            ExecutionModes.SET_REFERENCE: self._set_reference,
            ExecutionModes.SET_BASELINE: self._set_baseline,
            ExecutionModes.REPORT: self._report_similarity,
        }[mode]

    def _assert_similarity(self, candidate, assertion_id, threshold=None):
        ref_path = Path(ExecutionMode.reference_dir) / f"{self.reference_id}.json"
        data = self._load_json(ref_path, {"semantic_similarity": {}})
        entry = data["semantic_similarity"][assertion_id]

        score = self._cosim(candidate, entry["reference"])
        thr = (threshold if threshold is not None 
               else self.similarity_threshold if self.similarity_threshold is not None 
               else entry["suggested_threshold"])

        if score < thr:
            self._save_failure("semantic_similarity", {
                "assertion_id": assertion_id,
                "score": score,
                "threshold": thr,
                "candidate": candidate,
                "reference": entry["reference"]
            })
            raise AssertionError(f"{score} < {thr}")

        return score

    def _set_reference(self, candidate, assertion_id):
        ref_path = Path(ExecutionMode.reference_dir) / f"{self.reference_id}.json"
        data = self._load_json(ref_path, {"semantic_similarity": {}})
        data["semantic_similarity"][assertion_id] = {
            "reference": candidate,
            "scores": [],
            "mean": None,
            "std": None,
            "suggested_threshold": None,
        }
        self._save_json(ref_path, data)

    def _set_baseline(self, candidate, assertion_id):
        ref_path = Path(ExecutionMode.reference_dir) / f"{self.reference_id}.json"
        data = self._load_json(ref_path, {"semantic_similarity": {}})
        entry = data["semantic_similarity"][assertion_id]

        score = self._cosim(candidate, entry["reference"])
        entry["scores"].append(score)

        arr = np.array(entry["scores"])
        entry["mean"] = float(arr.mean())
        entry["std"] = float(arr.std()) if len(arr) > 1 else 0.0
        entry["suggested_threshold"] = float(entry["mean"] - (2 * entry["std"]))

        self._save_json(ref_path, data)
        return score

    def _report_similarity(self, candidate, assertion_id):
        ref_path = Path(ExecutionMode.reference_dir) / f"{self.reference_id}.json"
        data = self._load_json(ref_path, {"semantic_similarity": {}})
        entry = data["semantic_similarity"][assertion_id]

        score = self._cosim(candidate, entry["reference"])
        self._update_global("semantic_similarity", score)
        return score

    def _update_global(self, key, score):
        report_path = Path(ExecutionMode.report_file)
        data = self._load_json(report_path, {})

        if key not in data:
            data[key] = {"count": 0, "avg": 0.0}

        entry = data[key]
        c = entry["count"]
        entry["avg"] = (entry["avg"] * c + score) / (c + 1)
        entry["count"] = c + 1

        self._save_json(report_path, data)

    def _save_failure(self, metric_type, result):
        failures_path = Path(ExecutionMode.failures_file)
        data = self._load_json(failures_path, {"failures": []})
        data["failures"].append({
            "metric_type": metric_type,
            "result": result
        })
        self._save_json(failures_path, data)

    def _cosim(self, a, b):
        ea = np.array(self.embeds_service.embed(a)).reshape(1, -1)
        eb = np.array(self.embeds_service.embed(b)).reshape(1, -1)
        return float(cosine_similarity(ea, eb)[0][0])
    
    def criteria_check(
        self, content: str, criteria: List[str], threshold: Optional[float] = None
    ):
        result = self._criteria_check_handler(content, criteria)
        handler = self._criteria_handler(get_mode(), threshold)
        return handler(result)

    def _criteria_handler(self, mode, threshold=None):
        return {
            ExecutionModes.ASSERT: lambda result: self._assert_criteria(result, threshold),
            ExecutionModes.REPORT: self._report_criteria,
        }.get(mode, lambda result: result)

    def _assert_criteria(self, result, threshold=None):
        threshold = (threshold if threshold is not None 
                     else self.criteria_check_threshold if self.criteria_check_threshold is not None 
                     else ExecutionMode.default_thresholds.general_criteria) * 100
        if result["score"] < threshold:
            self._save_failure("criteria_check", result)
            raise AssertionError(f"Criteria check score {result['score']} < {threshold}")
        return result

    def _report_criteria(self, result):
        self._update_global("criteria_check", result["score"])
        return result

    def _criteria_check_handler(
        self, content: str, criteria: List[str]
    ):
        results = []

        for criterion in criteria:
            llm_judgement_result = self.llm_service.evaluate_criterion(
                criterion, content
            )
            results.append(llm_judgement_result)

        total_score = (
            len([result for result in results if result]) / len(criteria) * 100
        )
        result = {
            "score": total_score,
            "content": content,
            "criteria": [
                {"criterion": criteria[i], "result": results[i]}
                for i in range(len(criteria))
            ],
        }
        
        return result 


    async def claim_check(
        self,
        content: Optional[str],
        data_source: DataSource,
        threshold: Optional[float] = None,
        **kwargs
    ):
        result = await self._claim_check_handler(content, data_source, **kwargs)
        handler = self._claim_handler(get_mode(), threshold)
        return handler(result)

    def _claim_handler(self, mode, threshold=None):
        return {
            ExecutionModes.ASSERT: lambda result: self._assert_claim(result, threshold),
            ExecutionModes.REPORT: self._report_claim,
        }.get(mode, lambda result: result)

    def _assert_claim(self, result, threshold=None):
        threshold = (threshold if threshold is not None 
                     else self.claim_check_threshold if self.claim_check_threshold is not None 
                     else ExecutionMode.default_thresholds.claim_check) * 100
        if result["total_score"] < threshold:
            self._save_failure("claim_check", result)
            raise AssertionError(f"Claim check score {result['total_score']} < {threshold}")
        return result

    def _report_claim(self, result):
        self._update_global("claim_check", result["total_score"])
        return result

    async def _claim_check_handler(
        self,
        content: Optional[str],
        data_source: DataSource,
        **kwargs
    ) -> List[Dict[str, Union[str, bool]]]:
        claims = self.llm_service.extract_claims(content)

        call_args = self._collect_args(data_source, **kwargs)

        checker = self._get_checker(data_source)

        reference = await checker.fetch_reference(claims=claims, **call_args)

        chunked_reference = checker.chunk_content(reference)

        claim_check_result = checker.check_claims(claims=claims, content_chunks=chunked_reference)

        score = 0

        for claim in claim_check_result:
            if claim["validity"]:
                score += 1

        score = (score / len(claim_check_result)) * 100

        return {
            "total_score": score,
            "content": content,
            "claims": claim_check_result,
        }


    def _collect_args(self, data_source, **kwargs):
        args = {arg: kwargs.get(arg) for arg in data_source.required_args}
        missing = [k for k, v in args.items() if not v or (isinstance(v, str) and not v.strip())]
        if missing:
            raise ValueError(f"Missing required args for {data_source.name}: {missing}")
        return args
    
    def _get_checker(self, data_source: DataSource) -> ClaimChecker:
        checker_factory = {
            DataSource.WEB: lambda: WebChecker(self.llm_service),
            DataSource.MCP: lambda: MCPChecker(self.llm_service),
            DataSource.RETRIEVER: lambda: RetrieverChecker(self.llm_service),
        }

        return checker_factory[data_source]()
