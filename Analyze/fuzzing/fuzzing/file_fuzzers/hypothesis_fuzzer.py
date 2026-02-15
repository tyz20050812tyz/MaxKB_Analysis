"""
hypothesis_fuzzer.py - Property-based testing with Hypothesis (Fixed: /admin/api paths)
"""
import os, sys, json, argparse, requests
from datetime import datetime
from hypothesis import given, settings, strategies as st, HealthCheck

BASE_URL = "http://localhost:8080"
TOKEN = ""
RESULTS = []

def setup_config(base_url, token):
    global BASE_URL, TOKEN
    BASE_URL = base_url.rstrip('/')
    TOKEN = token

def api_request(method, path, json_body=None):
    url = BASE_URL + path
    headers = {"Authorization": TOKEN, "Content-Type": "application/json",
               "Accept": "application/json, text/plain, */*"}
    try:
        resp = requests.request(method, url, headers=headers, json=json_body,
                                timeout=30, verify=False, allow_redirects=False)
        try:
            rj = resp.json()
            return rj.get("code"), resp, rj
        except:
            return resp.status_code, resp, None
    except:
        return None, None, None

@given(
    name=st.text(min_size=0, max_size=5000),
    desc=st.text(min_size=0, max_size=10000),
)
@settings(max_examples=50, deadline=60000,
          suppress_health_check=[HealthCheck.too_slow])
def test_create_knowledge_robustness(name, desc):
    """Property: any name/desc should never cause code 500"""
    api_code, resp, rj = api_request("POST", "/admin/api/workspace/default/knowledge",
                                      json_body={"name": name, "desc": desc, "type": "0"})
    result = {
        "test": "create_knowledge", "name_length": len(name),
        "desc_length": len(desc), "api_code": api_code,
        "timestamp": datetime.now().isoformat(),
    }
    if api_code == 500:
        result["is_bug"] = True
        result["name_preview"] = repr(name[:100])
        result["desc_preview"] = repr(desc[:100])
        result["api_message"] = rj.get("message", "") if rj else ""
        print(f"  [BUG!] code=500 name_len={len(name)} desc_len={len(desc)} msg={result['api_message'][:80]}")
    else:
        result["is_bug"] = False
    RESULTS.append(result)

    # Cleanup: delete if created
    if api_code == 200 and rj and 'data' in rj:
        data = rj['data']
        if isinstance(data, dict) and 'id' in data:
            api_request("DELETE", f"/admin/api/workspace/default/knowledge/{data['id']}")

@given(query=st.text(min_size=0, max_size=2000))
@settings(max_examples=30, deadline=60000,
          suppress_health_check=[HealthCheck.too_slow])
def test_search_knowledge_robustness(query):
    """Property: any search query should never cause code 500"""
    encoded = requests.utils.quote(query)
    api_code, _, rj = api_request("GET", f"/admin/api/workspace/default/knowledge?name={encoded}")
    result = {
        "test": "search_knowledge", "query_length": len(query),
        "api_code": api_code, "is_bug": api_code == 500,
        "timestamp": datetime.now().isoformat(),
    }
    if result["is_bug"]:
        result["query_preview"] = repr(query[:100])
        result["api_message"] = rj.get("message", "") if rj else ""
        print(f"  [BUG!] code=500 query_len={len(query)}")
    RESULTS.append(result)

@given(
    method=st.sampled_from(["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]),
    path_suffix=st.text(min_size=1, max_size=200, alphabet=st.characters(
        whitelist_categories=('L', 'N'), whitelist_characters='-_/.'
    )),
)
@settings(max_examples=30, deadline=60000,
          suppress_health_check=[HealthCheck.too_slow])
def test_random_endpoint_robustness(method, path_suffix):
    """Property: random paths should return 404, never 500"""
    path = f"/admin/api/{path_suffix}"
    api_code, _, rj = api_request(method, path)
    result = {
        "test": "random_endpoint", "method": method, "path": path,
        "api_code": api_code, "is_bug": api_code == 500,
        "timestamp": datetime.now().isoformat(),
    }
    if result["is_bug"]:
        result["api_message"] = rj.get("message", "") if rj else ""
        print(f"  [BUG!] {method} {path} => code=500")
    RESULTS.append(result)

@given(
    data=st.recursive(
        st.none() | st.booleans() | st.integers() | st.floats(allow_nan=False) | st.text(max_size=100),
        lambda children: st.lists(children, max_size=5) | st.dictionaries(
            st.text(max_size=20), children, max_size=5
        ), max_leaves=20,
    )
)
@settings(max_examples=30, deadline=60000,
          suppress_health_check=[HealthCheck.too_slow])
def test_malformed_json_robustness(data):
    """Property: any JSON data should never cause code 500"""
    api_code, _, rj = api_request("POST", "/admin/api/workspace/default/knowledge", json_body=data)
    result = {
        "test": "malformed_json", "data_type": type(data).__name__,
        "api_code": api_code, "is_bug": api_code == 500,
        "timestamp": datetime.now().isoformat(),
    }
    if result["is_bug"]:
        result["api_message"] = rj.get("message", "") if rj else ""
        print(f"  [BUG!] Malformed JSON => code=500, type={type(data).__name__}")
    RESULTS.append(result)

def run_all_tests():
    print("=" * 70)
    print("MaxKB Hypothesis Property-Based Tests")
    print("=" * 70)
    print(f"Target: {BASE_URL}")
    print(f"API Prefix: /admin/api/")
    print(f"Time: {datetime.now().isoformat()}")

    # Verify connectivity
    api_code, _, rj = api_request("GET", "/admin/api/user/profile")
    if api_code == 200:
        print(f"[OK] Authenticated as: {rj['data'].get('username','')}")
    else:
        print(f"[WARNING] Auth check: code={api_code}")
    print()

    tests = [
        ("Create Knowledge - Random name/desc", test_create_knowledge_robustness),
        ("Search Knowledge - Random query", test_search_knowledge_robustness),
        ("Random Endpoint - Method/Path", test_random_endpoint_robustness),
        ("Malformed JSON - Random data", test_malformed_json_robustness),
    ]
    for name, test_func in tests:
        print(f"\n{'-'*60}")
        print(f"[*] Running: {name}")
        print(f"{'-'*60}")
        try:
            test_func()
            print(f"  [OK] Test completed")
        except Exception as e:
            print(f"  [FAIL] Test exception: {e}")
    return generate_report()

def generate_report():
    bugs = [r for r in RESULTS if r.get("is_bug")]
    report = {
        "meta": {"target": BASE_URL, "tool": "hypothesis",
                 "total_tests": len(RESULTS), "timestamp": datetime.now().isoformat()},
        "summary": {
            "total": len(RESULTS), "bugs_found": len(bugs), "by_test": {},
        },
        "bugs": bugs, "all_results": RESULTS,
    }
    for tn in set(r["test"] for r in RESULTS):
        t_results = [r for r in RESULTS if r["test"] == tn]
        report["summary"]["by_test"][tn] = {
            "total": len(t_results),
            "bugs": sum(1 for r in t_results if r.get("is_bug")),
        }
    os.makedirs("results", exist_ok=True)
    path = "results/hypothesis_fuzzing_report.json"
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 70)
    print("Hypothesis Property Test Report")
    print("=" * 70)
    print(f"Total tests: {report['summary']['total']}")
    print(f"Bugs found: {report['summary']['bugs_found']}")
    for tn, stats in report['summary']['by_test'].items():
        bug_str = f" [!!! {stats['bugs']} BUGS]" if stats['bugs'] else " [OK]"
        print(f"  {tn}: {stats['total']} cases{bug_str}")
    if bugs:
        print(f"\nBug Details:")
        for b in bugs[:20]:
            print(f"  [{b['test']}] code={b['api_code']} msg={b.get('api_message','')[:100]}")
    print(f"\nReport: {os.path.abspath(path)}")
    return report

def main():
    parser = argparse.ArgumentParser(description="MaxKB Hypothesis Tests")
    parser.add_argument("--base-url", default="http://localhost:8080")
    parser.add_argument("--token", required=True)
    args = parser.parse_args()
    setup_config(args.base_url, args.token)
    requests.packages.urllib3.disable_warnings()
    run_all_tests()

if __name__ == "__main__":
    main()
