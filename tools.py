"""HCLS MVP Search Tools with structured validation and local mock data fallback."""

import json
import os
from typing import Dict, Any, List
from pydantic import BaseModel, Field
import structlog

logger = structlog.get_logger()

# 1. Define explicit JSON schemas using Pydantic
class HCLSAcqQuery(BaseModel):
    account_name: str = Field(..., description="The HCLS account name. Must be 'Elevance Health' or 'Mayo Clinic'.")
    workload_type: str = Field(..., description="The target operational workload: 'prior_authorization', 'claims_processing', or 'clinical_search'.")

class SolutionRecommendation(BaseModel):
    account: str
    target_workload: str
    gcp_architecture: str
    deal_value: float
    compliance_impact: str

def query_hcls_mock_knowledge_base(query: HCLSAcqQuery) -> Dict[str, Any]:
    """Retrieves account metrics and pre-packaged GCP solutions from the mock dataset.
    
    Args:
        query: A validated Pydantic model containing account_name and workload_type.
        
    Returns:
        A dictionary containing the targeted solution recommendation or a recovery suggestion.
    """
    # Trace the intent in structured logs
    logger.info("tool_intent", tool="query_hcls_mock_knowledge_base", account=query.account_name, workload=query.workload_type)
    
    # Load the mock dataset file
    file_path = "mock_hcls_data.json"
    if not os.path.exists(file_path):
        return {
            "status": "error",
            "message": "Local mock knowledge base file not found.",
            "recovery_suggestion": "Ensure 'mock_hcls_data.json' exists in the root directory of the application."
        }
        
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            
        if query.account_name not in data:
            raise KeyError(f"Account '{query.account_name}' is not in the active top accounts database.")
            
        account_data = data[query.account_name]
        workloads = account_data.get("operational_bottlenecks", {})
        
        if query.workload_type not in workloads:
            valid_workloads = list(workloads.keys())
            raise ValueError(f"Workload '{query.workload_type}' not found. Valid options: {valid_workloads}")
            
        selected_workload = workloads[query.workload_type]
        
        # Format the successful payload matching our architecture schemas
        outcome = {
            "status": "success",
            "account": query.account_name,
            "workload": query.workload_type,
            "current_pain_point": selected_workload["current_pain_point"],
            "proposed_gcp_solution_play": selected_workload["gcp_solution_play"],
            "estimated_deal_value_usd": selected_workload["estimated_deal_value_usd"],
            "gcp_sales_stage": account_data["gcp_sales_stage"]
        }
        
        logger.info("tool_outcome", status="success", account=query.account_name, estimated_value=selected_workload["estimated_deal_value_usd"])
        return outcome

    except KeyError as ke:
        logger.error("tool_outcome", status="error", error=str(ke))
        return {
            "status": "error",
            "message": str(ke),
            "recovery_suggestion": "Try querying 'Elevance Health' or 'Mayo Clinic'."
        }
    except ValueError as ve:
        logger.error("tool_outcome", status="error", error=str(ve))
        return {
            "status": "error",
            "message": str(ve),
            "recovery_suggestion": f"Specify a valid workload. Run query with a workload like 'prior_authorization' or 'clinical_search'."
        }
