"""
test_api.py — Todo List API — Quick Test & Demo Script
=======================================================
Run this script to verify that every endpoint of the live
Todo API is working correctly.

Live URLs:
    API  (Railway)  → https://todo-api-test.up.railway.app
    UI   (Netlify)  → https://todo-api-test.netlify.app

Requirements:
    pip install requests

Usage:
    Simply run:
        python test_api.py

    To test a different API host:
        python test_api.py --base-url https://your-api-url.com
"""

import sys
import json
import argparse
import requests

# ── Config ────────────────────────────────────────────────────────────────────

DEFAULT_BASE_URL = "https://todo-api-test.up.railway.app"
FRONTEND_URL    = "https://todo-api-test.netlify.app"

# ── Helpers ───────────────────────────────────────────────────────────────────

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

passed = 0
failed = 0


def header(title: str):
    print(f"\n{BOLD}{CYAN}{'─' * 60}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'─' * 60}{RESET}")


def check(label: str, condition: bool, extra: str = ""):
    global passed, failed
    if condition:
        passed += 1
        status = f"{GREEN}✔  PASS{RESET}"
    else:
        failed += 1
        status = f"{RED}✘  FAIL{RESET}"
    print(f"  {status}  {label}")
    if extra:
        print(f"         {YELLOW}{extra}{RESET}")


def pretty(data) -> str:
    return json.dumps(data, indent=4, ensure_ascii=False)


# ── Test Suite ─────────────────────────────────────────────────────────────────

def run_tests(base: str):
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})

    created_id = None   # will store the ID of a todo created during the test

    # ── 1. Health Check ───────────────────────────────────────────────────────
    header("1 · Health Check  GET /")
    try:
        r = session.get(f"{base}/")
        print(f"  Status : {r.status_code}")
        print(f"  Body   : {pretty(r.json())}")
        check("Status is 200", r.status_code == 200)
        check("Response contains 'message'", "message" in r.json())
    except requests.exceptions.ConnectionError:
        print(f"\n  {RED}ERROR: Could not connect to {base}{RESET}")
        print(f"  Make sure the API is running:  uvicorn main:app --reload\n")
        sys.exit(1)

    # ── 2. List All Todos (initially empty) ───────────────────────────────────
    header("2 · List Todos  GET /todos")
    r = session.get(f"{base}/todos")
    print(f"  Status : {r.status_code}")
    print(f"  Body   : {pretty(r.json())}")
    check("Status is 200", r.status_code == 200)
    check("Response is a list", isinstance(r.json(), list))

    # ── 3. Create a New Todo ──────────────────────────────────────────────────
    header("3 · Create Todo  POST /todos")
    payload = {
        "title": "Review API test script",
        "description": "Make sure all endpoints return correct data",
        "priority": "high",
        "due_date": "2026-12-31"
    }
    r = session.post(f"{base}/todos", json=payload)
    print(f"  Status : {r.status_code}")
    print(f"  Body   : {pretty(r.json())}")
    check("Status is 201 Created", r.status_code == 201)
    check("'id' field present", "id" in r.json())
    check("Title matches payload", r.json().get("title") == payload["title"])
    check("Done defaults to false", r.json().get("done") == False)

    if r.status_code == 201:
        created_id = r.json()["id"]
        print(f"\n  {YELLOW}Saved todo ID: {created_id}{RESET}")

    # ── 4. Get Single Todo ────────────────────────────────────────────────────
    header(f"4 · Get Single Todo  GET /todos/{{id}}")
    if created_id:
        r = session.get(f"{base}/todos/{created_id}")
        print(f"  Status : {r.status_code}")
        print(f"  Body   : {pretty(r.json())}")
        check("Status is 200", r.status_code == 200)
        check("ID matches", r.json().get("id") == created_id)
    else:
        check("Skipped — no todo was created", False, "Previous step failed")

    # ── 5. Get Non-Existent Todo (expects 404) ────────────────────────────────
    header("5 · Get Non-Existent Todo  GET /todos/invalid-id")
    r = session.get(f"{base}/todos/invalid-id-that-does-not-exist")
    print(f"  Status : {r.status_code}")
    print(f"  Body   : {pretty(r.json())}")
    check("Status is 404 Not Found", r.status_code == 404)

    # ── 6. Partial Update — Mark as Done (PATCH) ──────────────────────────────
    header(f"6 · Partial Update  PATCH /todos/{{id}}")
    if created_id:
        r = session.patch(f"{base}/todos/{created_id}", json={"done": True})
        print(f"  Status : {r.status_code}")
        print(f"  Body   : {pretty(r.json())}")
        check("Status is 200", r.status_code == 200)
        check("'done' is now true", r.json().get("done") == True)
        check("Title unchanged", r.json().get("title") == payload["title"])
    else:
        check("Skipped — no todo was created", False, "Previous step failed")

    # ── 7. Full Update (PUT) ──────────────────────────────────────────────────
    header(f"7 · Full Update  PUT /todos/{{id}}")
    if created_id:
        full_payload = {
            "title": "Updated title by boss",
            "description": "Full PUT update test",
            "done": False,
            "priority": "medium",
            "due_date": None
        }
        r = session.put(f"{base}/todos/{created_id}", json=full_payload)
        print(f"  Status : {r.status_code}")
        print(f"  Body   : {pretty(r.json())}")
        check("Status is 200", r.status_code == 200)
        check("Title updated", r.json().get("title") == full_payload["title"])
        check("Priority updated", r.json().get("priority") == "medium")
        check("Done reset to false", r.json().get("done") == False)
    else:
        check("Skipped — no todo was created", False, "Previous step failed")

    # ── 8. Filter — List by Priority ─────────────────────────────────────────
    header("8 · Filter by Priority  GET /todos?priority=medium")
    r = session.get(f"{base}/todos", params={"priority": "medium"})
    print(f"  Status : {r.status_code}")
    print(f"  Body   : {pretty(r.json())}")
    check("Status is 200", r.status_code == 200)
    check("All returned items have priority=medium",
          all(t["priority"] == "medium" for t in r.json()))

    # ── 9. Search Keyword Filter ──────────────────────────────────────────────
    header("9 · Search Keyword  GET /todos?search=boss")
    r = session.get(f"{base}/todos", params={"search": "boss"})
    print(f"  Status : {r.status_code}")
    print(f"  Body   : {pretty(r.json())}")
    check("Status is 200", r.status_code == 200)
    check("Results contain the keyword 'boss' in title or description",
          all("boss" in (t["title"] + (t.get("description") or "")).lower()
              for t in r.json()))

    # ── 10. Create a Second Todo and Mark Done ────────────────────────────────
    header("10 · Create 2nd Todo + Mark Done  (setup for clear-completed)")
    r2 = session.post(f"{base}/todos", json={"title": "Completed task to delete", "priority": "low"})
    second_id = r2.json().get("id") if r2.status_code == 201 else None
    check("Second todo created (201)", r2.status_code == 201)

    if second_id:
        rp = session.patch(f"{base}/todos/{second_id}", json={"done": True})
        check("Second todo marked as done", rp.json().get("done") == True)

    # ── 11. Delete Single Todo ────────────────────────────────────────────────
    header(f"11 · Delete Single Todo  DELETE /todos/{{id}}")
    if created_id:
        r = session.delete(f"{base}/todos/{created_id}")
        print(f"  Status : {r.status_code}")
        check("Status is 204 No Content", r.status_code == 204)

        # Confirm it's gone
        r = session.get(f"{base}/todos/{created_id}")
        check("Deleted todo returns 404", r.status_code == 404)
    else:
        check("Skipped — no todo was created", False, "Previous step failed")

    # ── 12. Clear All Completed Todos ─────────────────────────────────────────
    header("12 · Clear Completed  DELETE /todos")
    r = session.delete(f"{base}/todos")
    print(f"  Status : {r.status_code}")
    print(f"  Body   : {pretty(r.json())}")
    check("Status is 200", r.status_code == 200)
    check("'deleted' field in response", "deleted" in r.json())
    check("At least 1 completed todo was removed", r.json().get("deleted", 0) >= 1)

    # ── Summary ───────────────────────────────────────────────────────────────
    total = passed + failed
    print(f"\n{BOLD}{'═' * 60}{RESET}")
    print(f"{BOLD}  TEST SUMMARY{RESET}")
    print(f"{'═' * 60}")
    print(f"  Total  : {total}")
    print(f"  {GREEN}Passed : {passed}{RESET}")
    print(f"  {RED if failed else GREEN}Failed : {failed}{RESET}")
    print(f"{'═' * 60}\n")

    if failed == 0:
        print(f"  {GREEN}{BOLD}🎉  All tests passed! The API is working correctly.{RESET}\n")
    else:
        print(f"  {RED}{BOLD}⚠️   Some tests failed. Please review the output above.{RESET}\n")

    return failed == 0


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Todo API Test Script")
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"Base URL of the running API (default: {DEFAULT_BASE_URL})"
    )
    args = parser.parse_args()

    print(f"\n{BOLD}Todo List API — Test Suite{RESET}")
    print(f"  API  : {CYAN}{args.base_url}{RESET}")
    print(f"  UI   : {CYAN}{FRONTEND_URL}{RESET}")

    success = run_tests(args.base_url)
    sys.exit(0 if success else 1)
