#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Save research report to Get笔记 and add to knowledge base.

Usage:
    python save_to_getnote.py <title> <content_file> [knowledge_id]

Arguments:
    title           Note title
    content_file    Path to the markdown file to save
    knowledge_id    Knowledge base ID (default: eYxz6N4J)

Environment Variables:
    GETNOTE_API_KEY     Get笔记 API key (gk_live_xxx)
    GETNOTE_CLIENT_ID   Get笔记 Client ID (cli_xxx)

Example:
    python save_to_getnote.py "【横纵分析】Claude Code" ./claude_code.md
    python save_to_getnote.py "【横纵分析】MCP协议" ./mcp.md abc123
"""

import json
import os
import sys
import urllib.request
import urllib.error


def get_api_credentials():
    """Get API credentials from environment variables."""
    api_key = os.environ.get('GETNOTE_API_KEY')
    client_id = os.environ.get('GETNOTE_CLIENT_ID')

    if not api_key or not client_id:
        print('Error: GETNOTE_API_KEY and GETNOTE_CLIENT_ID environment variables are required')
        sys.exit(1)

    return api_key, client_id


def make_request(url, data, api_key, client_id):
    """Make HTTP request to Get笔记 API."""
    headers = {
        'Authorization': api_key,
        'X-Client-ID': client_id,
        'Content-Type': 'application/json'
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers=headers
    )
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.URLError as e:
        return {'success': False, 'error': str(e)}


def save_note(title, content, api_key, client_id):
    """Save note to Get笔记."""
    save_data = {
        'title': title,
        'content': content,
        'note_type': 'plain_text',
        'tags': ['卡兹克纵横分析法', 'Deep Research', '自动生成']
    }

    result = make_request(
        'https://openapi.biji.com/open/api/v1/resource/note/save',
        save_data,
        api_key,
        client_id
    )

    if result.get('success'):
        note_id = str(result['data']['note_id'])
        print('Note saved successfully, ID:', note_id)
        return note_id
    else:
        print('Save failed:', result)
        return None


def add_to_knowledge_base(note_id, knowledge_id, api_key, client_id):
    """Add note to knowledge base."""
    result = make_request(
        'https://openapi.biji.com/open/api/v1/resource/knowledge/note/batch-add',
        {'topic_id': knowledge_id, 'note_ids': [note_id]},
        api_key,
        client_id
    )

    if result.get('success'):
        print('Added to knowledge base successfully')
        return True
    else:
        print('Failed to add to knowledge base:', result)
        return False


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    title = sys.argv[1]
    content_file = sys.argv[2]
    knowledge_id = sys.argv[3] if len(sys.argv) > 3 else 'eYxz6N4J'

    # Read content file
    try:
        with open(content_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print('Error: File not found:', content_file)
        sys.exit(1)
    except UnicodeDecodeError:
        print('Error: File encoding is not UTF-8')
        sys.exit(1)

    print('Content length:', len(content), 'characters')

    # Get API credentials
    api_key, client_id = get_api_credentials()

    # Save note
    note_id = save_note(title, content, api_key, client_id)
    if not note_id:
        sys.exit(1)

    # Add to knowledge base
    add_to_knowledge_base(note_id, knowledge_id, api_key, client_id)

    print('Done!')
    return note_id


if __name__ == '__main__':
    main()
