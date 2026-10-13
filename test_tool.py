from tools import query_hcls_mock_knowledge_base, HCLSAcqQuery

# Test Case 1: Valid retrieval for Elevance Health
query_valid = HCLSAcqQuery(account_name="Elevance Health", workload_type="prior_authorization")
print("--- VALID RETRIEVED DATA ---")
print(query_hcls_mock_knowledge_base(query_valid))

# Test Case 2: Invalid workload (Triggers Guided Error Handling)
query_invalid = HCLSAcqQuery(account_name="Elevance Health", workload_type="clinical_search")
print("\n--- GUIDED ERROR RECOVERY DATA ---")
print(query_hcls_mock_knowledge_base(query_invalid))

