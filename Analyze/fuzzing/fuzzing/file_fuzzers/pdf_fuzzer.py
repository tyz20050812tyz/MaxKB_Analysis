"""
pdf_fuzzer.py - MaxKB File Upload Fuzzer (Fixed: correct API paths)
"""
import os, sys, json, time, argparse, requests
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from malformed_generator import MalformedFileGenerator

class FileUploadFuzzer:
    MIME_TYPES = {
        '.pdf': 'application/pdf',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.md': 'text/markdown', '.txt': 'text/plain', '.html': 'text/html',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    }

    def __init__(self, base_url, token, dataset_id, results_dir="results"):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.dataset_id = dataset_id
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": token,
            "Accept": "application/json, text/plain, */*",
        })
        self.session.verify = False
        requests.packages.urllib3.disable_warnings()
        self.results = []
        self.upload_endpoint = None

    def discover_endpoint(self):
        print("[*] Discovering MaxKB upload endpoints...")
        DS = self.dataset_id
        candidates = [
            f"/admin/api/workspace/default/knowledge/{DS}/document",
            f"/admin/api/workspace/default/knowledge/{DS}/document/upload",
            f"/admin/api/workspace/default/knowledge/{DS}/document/web",
            f"/admin/api/workspace/default/knowledge/{DS}/file",
            f"/admin/api/dataset/{DS}/document",
        ]

        # First verify knowledge base exists
        check_url = f"{self.base_url}/admin/api/workspace/default/knowledge/{DS}"
        try:
            resp = self.session.get(check_url, allow_redirects=False, timeout=10)
            rj = resp.json() if 'json' in resp.headers.get('Content-Type','') else {}
            print(f"  Knowledge base check: HTTP {resp.status_code}, code={rj.get('code','N/A')}")
            if rj.get('code') == 200:
                print(f"    [OK] Knowledge base found: {rj.get('data',{}).get('name','')}")
        except Exception as e:
            print(f"  Knowledge base check failed: {e}")

        # Try upload endpoints
        for ep in candidates:
            url = self.base_url + ep
            try:
                files = {'file': ('test.txt', b"fuzzing test content", 'text/plain')}
                resp = self.session.post(url, files=files, allow_redirects=False, timeout=10)
                ct = resp.headers.get('Content-Type', '')
                is_json = 'json' in ct
                rj = resp.json() if is_json else {}
                api_code = rj.get('code', 'N/A')
                print(f"  POST {ep}")
                print(f"    => HTTP {resp.status_code}, code={api_code}, json={is_json}")
                if is_json and api_code != 404:
                    self.upload_endpoint = ep
                    print(f"    [OK] Found upload endpoint!")
                    if api_code != 200:
                        print(f"    Response: {json.dumps(rj, ensure_ascii=False)[:200]}")
                    return ep
            except Exception as e:
                print(f"  POST {ep} => Error: {e}")

        if not self.upload_endpoint:
            print("[!] No upload endpoint found, using default")
            self.upload_endpoint = candidates[0]
        return self.upload_endpoint

    def upload_file(self, filepath):
        filename = os.path.basename(filepath)
        ext = os.path.splitext(filename)[1].lower()
        mime_type = self.MIME_TYPES.get(ext, 'application/octet-stream')
        url = self.base_url + self.upload_endpoint
        result = {
            "file": filename, "file_size": os.path.getsize(filepath),
            "mime_type": mime_type, "endpoint": self.upload_endpoint,
            "timestamp": datetime.now().isoformat(),
        }
        try:
            with open(filepath, 'rb') as f:
                files = {'file': (filename, f, mime_type)}
                t0 = time.time()
                resp = self.session.post(url, files=files, allow_redirects=False, timeout=60)
                elapsed = time.time() - t0
                result["http_status"] = resp.status_code
                result["response_time"] = round(elapsed, 3)

                # Parse JSON response
                try:
                    rj = resp.json()
                    result["api_code"] = rj.get("code")
                    result["api_message"] = rj.get("message", "")
                    result["response_body"] = rj
                except:
                    result["response_body"] = resp.text[:500]
                    result["api_code"] = None

                api_code = result.get("api_code")

                # Check for bugs: API code 500 or HTTP 5xx
                if api_code == 500 or resp.status_code >= 500:
                    result["is_bug"] = True
                    result["bug_type"] = "SERVER_ERROR"
                    msg = result.get("api_message", "")[:80]
                    print(f"  [BUG!] {filename} => code={api_code} msg={msg}")
                elif elapsed > 30:
                    result["is_bug"] = True
                    result["bug_type"] = "TIMEOUT"
                    print(f"  [BUG!] {filename} => Slow ({elapsed:.1f}s)")
                elif api_code == 200:
                    result["is_bug"] = False
                    print(f"  [OK] {filename} => code={api_code} ({elapsed:.2f}s)")
                else:
                    result["is_bug"] = False
                    print(f"  [REJECTED] {filename} => code={api_code} ({elapsed:.2f}s)")

        except requests.exceptions.Timeout:
            result.update({"http_status": "TIMEOUT", "response_time": 60,
                           "is_bug": True, "bug_type": "TIMEOUT"})
            print(f"  [BUG!] {filename} => Timeout (60s)")
        except requests.exceptions.ConnectionError as e:
            result.update({"http_status": "CONNECTION_ERROR", "error": str(e)[:200],
                           "is_bug": True, "bug_type": "CRASH"})
            print(f"  [BUG!] {filename} => Connection error (possible crash)")
        except Exception as e:
            result.update({"http_status": "ERROR", "error": str(e)[:200], "is_bug": False})
            print(f"  [FAIL] {filename} => {str(e)[:80]}")

        self.results.append(result)
        return result

    def run_fuzzing(self, file_dir="malformed_files"):
        print("=" * 70)
        print("MaxKB File Upload Fuzzer")
        print("=" * 70)
        print(f"Target: {self.base_url}")
        print(f"API Prefix: /admin/api/workspace/default/knowledge/")
        print(f"Dataset ID: {self.dataset_id}")
        print()
        self.discover_endpoint()
        print()
        if not os.path.exists(file_dir):
            print("[*] Generating malformed files...")
            MalformedFileGenerator(file_dir).generate_all()
            print()
        test_files = sorted([
            os.path.join(file_dir, f) for f in os.listdir(file_dir)
            if os.path.isfile(os.path.join(file_dir, f))
        ])
        print(f"[*] Found {len(test_files)} test files\n")
        print("[*] Starting upload tests...")
        print("-" * 70)
        for i, fp in enumerate(test_files, 1):
            print(f"[{i}/{len(test_files)}]", end="")
            self.upload_file(fp)
            time.sleep(1)
        self.generate_report()

    def generate_report(self):
        bugs = [r for r in self.results if r.get("is_bug")]
        report = {
            "meta": {"target": self.base_url, "dataset_id": self.dataset_id,
                     "upload_endpoint": self.upload_endpoint,
                     "total_tests": len(self.results),
                     "timestamp": datetime.now().isoformat()},
            "summary": {
                "total": len(self.results),
                "bugs_found": len(bugs),
                "server_errors": sum(1 for r in bugs if r.get("bug_type") == "SERVER_ERROR"),
                "timeouts": sum(1 for r in bugs if r.get("bug_type") == "TIMEOUT"),
                "crashes": sum(1 for r in bugs if r.get("bug_type") == "CRASH"),
                "api_code_distribution": {},
            },
            "bugs": bugs,
            "all_results": self.results,
        }
        for r in self.results:
            code = str(r.get("api_code", r.get("http_status", "UNKNOWN")))
            report["summary"]["api_code_distribution"][code] = \
                report["summary"]["api_code_distribution"].get(code, 0) + 1

        rp = os.path.join(self.results_dir, "file_fuzzing_report.json")
        with open(rp, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        s = report['summary']
        print("\n" + "=" * 70)
        print("File Upload Fuzzing Report")
        print("=" * 70)
        print(f"Total: {s['total']} | Bugs: {s['bugs_found']} | 5xx: {s['server_errors']} | Timeouts: {s['timeouts']} | Crashes: {s['crashes']}")
        print(f"\nAPI code distribution:")
        for code, cnt in sorted(s['api_code_distribution'].items()):
            print(f"  {code}: {cnt}")
        if bugs:
            print(f"\nBug Details:")
            for b in bugs:
                print(f"  {b['file']} => code={b.get('api_code')} type={b.get('bug_type')} msg={b.get('api_message','')[:100]}")
        print(f"\nReport: {os.path.abspath(rp)}")

def main():
    p = argparse.ArgumentParser(description="MaxKB File Upload Fuzzer")
    p.add_argument("--base-url", default="http://localhost:8080")
    p.add_argument("--token", required=True)
    p.add_argument("--dataset-id", required=True)
    p.add_argument("--file-dir", default="malformed_files")
    p.add_argument("--results-dir", default="results")
    a = p.parse_args()
    FileUploadFuzzer(a.base_url, a.token, a.dataset_id, a.results_dir).run_fuzzing(a.file_dir)

if __name__ == "__main__":
    main()
