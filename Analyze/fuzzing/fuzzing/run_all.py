"""
run_all.py - MaxKB Fuzzing Master Runner
"""
import os, sys, argparse, time
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'file_fuzzers'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api_fuzzers'))

def run_file_fuzzing(base_url, token, dataset_id, results_dir):
    print("\n" + "#" * 70)
    print("#  Stage 1: Malformed File Generation & Upload Fuzzing")
    print("#" * 70)
    from file_fuzzers.malformed_generator import MalformedFileGenerator
    from file_fuzzers.pdf_fuzzer import FileUploadFuzzer
    file_dir = os.path.join(os.path.dirname(__file__), "malformed_files")
    MalformedFileGenerator(file_dir).generate_all()
    FileUploadFuzzer(base_url, token, dataset_id, results_dir).run_fuzzing(file_dir)

def run_api_fuzzing(base_url, token, dataset_id, results_dir):
    print("\n" + "#" * 70)
    print("#  Stage 2: API Security Fuzzing")
    print("#" * 70)
    from api_fuzzers.knowledge_base_fuzzer import KnowledgeBaseFuzzer
    KnowledgeBaseFuzzer(base_url, token, dataset_id, results_dir).run_all_tests()

def run_hypothesis_fuzzing(base_url, token, results_dir):
    print("\n" + "#" * 70)
    print("#  Stage 3: Hypothesis Property-Based Testing")
    print("#" * 70)
    from file_fuzzers.hypothesis_fuzzer import setup_config, run_all_tests
    import requests
    requests.packages.urllib3.disable_warnings()
    setup_config(base_url, token)
    run_all_tests()

def main():
    p = argparse.ArgumentParser(description="MaxKB Fuzzing Master Runner")
    p.add_argument("--base-url", default="http://localhost:8080")
    p.add_argument("--token", required=True)
    p.add_argument("--dataset-id", default="")
    p.add_argument("--results-dir", default="results")
    p.add_argument("--only", choices=["file","api","hypothesis","all"], default="all")
    a = p.parse_args()
    rd = os.path.join(os.path.dirname(__file__), a.results_dir)
    os.makedirs(rd, exist_ok=True)
    print("=" * 70)
    print("MaxKB Security & Robustness Fuzzing Test Suite")
    print("=" * 70)
    print(f"Target: {a.base_url}")
    print(f"Time: {datetime.now().isoformat()}")
    print(f"Mode: {a.only}\n")
    t0 = time.time()
    if a.only in ["file","all"]:
        if not a.dataset_id: print("[!] File fuzzing requires --dataset-id")
        else: run_file_fuzzing(a.base_url, a.token, a.dataset_id, rd)
    if a.only in ["api","all"]:
        if not a.dataset_id: print("[!] API fuzzing requires --dataset-id")
        else: run_api_fuzzing(a.base_url, a.token, a.dataset_id, rd)
    if a.only in ["hypothesis","all"]:
        run_hypothesis_fuzzing(a.base_url, a.token, rd)
    print(f"\n{'='*70}")
    print(f"All tests done! Time: {time.time()-t0:.1f}s")
    print(f"Reports: {os.path.abspath(rd)}")
    print("=" * 70)
    if os.path.exists(rd):
        for r in sorted(f for f in os.listdir(rd) if f.endswith('.json')):
            print(f"  {r} ({os.path.getsize(os.path.join(rd,r)):,} bytes)")

if __name__ == "__main__":
    main()
