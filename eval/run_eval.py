import json
import os
import httpx

BASE_URL = os.getenv("RAG_BASE_URL", "http://localhost:8000")
USERNAME = os.getenv("RAG_USERNAME", "admin")
PASSWORD = os.getenv("RAG_PASSWORD", "change-this-now")

def get_token(client: httpx.Client) -> str:
    response = client.post(f"{BASE_URL}/auth/token", data={"username": USERNAME, "password": PASSWORD})
    response.raise_for_status()
    return response.json()["access_token"]

def main() -> None:
    with open("eval/questions.json", encoding="utf-8") as fh:
        cases = json.load(fh)
    passed = 0
    with httpx.Client(timeout=180.0) as client:
        token = get_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        for case in cases:
            response = client.post(f"{BASE_URL}/query", headers=headers, json={"question": case["question"]})
            response.raise_for_status()
            data = response.json()
            keyword_ok = case["expected_keyword"].lower() in data["answer"].lower()
            abstention_ok = data["abstained"] is case["expect_abstention"]
            citation_ok = data["citation_valid"]
            source_ok = True if case["expected_source"] is None else any(c["filename"] == case["expected_source"] for c in data["citations"])
            ok = keyword_ok and abstention_ok and citation_ok and source_ok
            passed += int(ok)
            print(f"{'PASS' if ok else 'FAIL'} | {case['question']}")
    total = len(cases)
    print(f"Evaluation score: {passed}/{total} = {passed / total:.1%}")

if __name__ == "__main__":
    main()
