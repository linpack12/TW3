"""COMPLETE DEMO: Part 1 - MCP Server"""

import requests
from pprint import pprint

BASE = "http://127.0.0.1:8000/mcp/tools/call"

def call_tool(tool:str, params: dict):
    resp = requests.post(BASE, json={"tool": tool, "params": params}, timeout=10,)
    resp.raise_for_status()
    return resp.json()

def main():
    # Navigate to URL
    print("1) Navigate to https://example.com")
    navigate_response = call_tool("navigate", {"url": "https://example.com"})
    pprint(navigate_response)

    # Take screenshot of viewport 
    print("\n2) Take screenshot (viewport only)")
    screenshot_response = call_tool("screenshot", {"full_page": False})
    pprint(screenshot_response)

    # Extract links 
    print("\n3) Extract links")
    extract_link_response = call_tool("extract_links", {})
    pprint(extract_link_response)

    links = extract_link_response.get("data", [])
    if not links:
        print("No links found, aborting")
        return
    
    first_link = links[0]["href"]
    # Navigate to first link
    print(f"\n4) Navigate to first link: {first_link}")
    navigate_to_link_response = call_tool("navigate", {"url": first_link})
    pprint(navigate_to_link_response)

    # Take a screenshot of the full page
    print("\n5) Take second screenshot (full page)")
    screenshot_full_page_response = call_tool("screenshot", {"full_page": True})
    pprint(screenshot_full_page_response)

if __name__ == "__main__":
    main()

