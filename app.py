import os
import sys
import json
import re
import traceback
import logging
from flask import Flask, request, jsonify, send_from_directory, Response
from werkzeug.utils import secure_filename

# Ensure current module directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from search_tool import search_web
from summarizer import summarize_text, summarize_text_short
from document_processor import read_document
from genai_client import ask_gemini, set_api_key, is_key_configured, get_api_key
from scraper import scrape_text
from memory import Memory
from research_summarizer import summarize_research

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("DeepResearchAgent")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_FOLDER = os.path.join(BASE_DIR, 'frontend')
UPLOADS_FOLDER = os.path.join(BASE_DIR, 'uploads')
SESSIONS_FOLDER = os.path.join(BASE_DIR, 'sessions')

os.makedirs(UPLOADS_FOLDER, exist_ok=True)
os.makedirs(SESSIONS_FOLDER, exist_ok=True)

app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path='')
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max upload limit

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for cloud platforms and uptime monitors."""
    return jsonify({
        "status": "healthy",
        "service": "Deep Research AI Agent",
        "api_key_configured": is_key_configured()
    }), 200

@app.route("/api/config", methods=["GET"])
def get_config():
    """Returns current environment capabilities."""
    key = get_api_key()
    has_key = is_key_configured()
    masked_key = f"{key[:6]}...{key[-4:]}" if has_key and len(key) > 10 else ""
    return jsonify({
        "api_key_configured": has_key,
        "masked_key": masked_key,
        "active_models": ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
    })

@app.route("/api/set_key", methods=["POST"])
def update_key():
    """Dynamically updates the Gemini API key from the frontend settings."""
    try:
        data = request.get_json(force=True, silent=True) or {}
        key = data.get("api_key", "").strip()
        if not key:
            return jsonify({"error": "No API key provided"}), 400
        
        set_api_key(key)
        
        # Persist key into .env
        env_file = os.path.join(BASE_DIR, '.env')
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(f'GEMINI_API_KEY="{key}"\n')
            
        return jsonify({"status": "success", "message": "API key successfully updated and saved."})
    except Exception as e:
        logger.error(f"Error setting API key: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_input = request.form.get("user_input", "").strip()
        chat_id_str = request.form.get("chat_id")
        mode = request.form.get("mode", "chat")  # 'chat' or 'deep_research'
        
        if chat_id_str and chat_id_str.strip():
            try:
                current_chat_id = int(chat_id_str)
            except ValueError:
                current_chat_id = chat_id_str
        else:
            # Generate next numeric chat ID
            existing_ids = []
            for fname in os.listdir(SESSIONS_FOLDER):
                if fname.endswith(".json"):
                    base = fname.split('.')[0]
                    if base.isdigit():
                        existing_ids.append(int(base))
            current_chat_id = max(existing_ids, default=-1) + 1
        
        memory = Memory(current_chat_id, storage_path=SESSIONS_FOLDER)
        
        # Handle file attachments
        files = request.files.getlist('file')
        file_content = ''
        uploaded_file_names = []
        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOADS_FOLDER, filename)
                file.save(file_path)
                text = read_document(file_path)
                if text:
                    file_content += f"\n--- Content of {filename} ---\n{text}\n"
                    uploaded_file_names.append(filename)
        
        if file_content:
            memory.add_message('context', file_content)
            user_input = f"[Attached: {', '.join(uploaded_file_names)}]\n{user_input}" if user_input else f"Please analyze and summarize the attached document(s): {', '.join(uploaded_file_names)}"

        # If user explicitly selected 'deep_research' mode or input is a research prompt
        if mode == 'deep_research' or user_input.lower().startswith("research:") or user_input.lower().startswith("/research"):
            clean_topic = re.sub(r'^(research:?|/research)\s*', '', user_input, flags=re.IGNORECASE).strip()
            if not clean_topic:
                clean_topic = user_input

            research_report, papers = summarize_research(clean_topic)
            short_summary = summarize_text_short(research_report)

            assistant_response_content = {
                'body': research_report,
                'summary': short_summary,
                'research_papers': papers,
                'mode': 'deep_research'
            }

            memory.add_message('user', user_input)
            memory.add_message('assistant', assistant_response_content)

            return jsonify({
                'assistant_message': {'content': assistant_response_content},
                'chat_id': current_chat_id
            })

        # URL detection and automatic web scraping
        url_match = re.search(r'https?://[^\s]+', user_input)
        if url_match:
            url = url_match.group(0)
            scraped_text = scrape_text(url)
            if scraped_text:
                memory.add_message('context', f"Scraped content from {url}:\n{scraped_text}")
                
                # Check if there is an accompanying question with the URL
                remaining_query = user_input.replace(url, '').strip()
                if not remaining_query:
                    # Provide an immediate executive overview of the URL
                    overview = summarize_text(scraped_text)
                    assistant_response_content = {
                        'body': f"### Web Intelligence Extracted: [{url}]({url})\n\n{overview}\n\n*You can now ask follow-up questions regarding this page.*",
                        'summary': f"Successfully extracted and analyzed web content from {url}.",
                        'research_papers': [{'title': url, 'href': url, 'source': 'Web Page'}]
                    }
                    memory.add_message('user', user_input)
                    memory.add_message('assistant', assistant_response_content)
                    return jsonify({
                        'assistant_message': {'content': assistant_response_content},
                        'chat_id': current_chat_id
                    })
            else:
                assistant_response_content = {
                    'body': f"I was unable to retrieve readable text from `{url}`. The site may have strict bot protection or require JavaScript rendering.",
                    'summary': "URL retrieval failed.",
                    'research_papers': []
                }
                memory.add_message('user', user_input)
                memory.add_message('assistant', assistant_response_content)
                return jsonify({
                    'assistant_message': {'content': assistant_response_content},
                    'chat_id': current_chat_id
                })

        # Contextual Question Answering
        conversation_history = memory.get_history()
        context = ""
        for msg in conversation_history:
            if msg.get('role') == 'context':
                context += str(msg.get('content', '')) + "\n\n"
        
        if user_input:
            # Query web/arXiv papers if relevant
            supplementary_papers = []
            if len(user_input.split()) > 2 and ("how" in user_input.lower() or "what" in user_input.lower() or "why" in user_input.lower() or "compare" in user_input.lower()):
                supplementary_papers = search_web(user_input, max_results=3, include_academic=True)

            history_tuples = []
            for msg in conversation_history:
                if msg.get('role') in ['user', 'assistant']:
                    c = msg.get('content')
                    text_c = c.get('body') if isinstance(c, dict) else str(c)
                    history_tuples.append(f"{msg.get('role').upper()}: {text_c[:300]}")

            prompt = f"""You are an advanced Deep Research AI Assistant. Answer the user's question clearly, thoroughly, and objectively.

Context Documents & Extracted Web Data:
{context[:10000]}

Conversation History:
{chr(10).join(history_tuples[-6:])}

User Question:
{user_input}

Provide a well-structured response using Markdown (with clear headings, bullet points, and code formatting where applicable).
"""
            
            output_text = ask_gemini(prompt, chat_history=conversation_history)
            short_summary = summarize_text_short(output_text, chat_history=conversation_history)

            assistant_response_content = {
                'body': output_text,
                'summary': short_summary,
                'research_papers': supplementary_papers
            }

            memory.add_message('user', user_input)
            memory.add_message('assistant', assistant_response_content)

            return jsonify({
                'assistant_message': {'content': assistant_response_content},
                'chat_id': current_chat_id
            })

    except Exception as e:
        logger.error(f"Error in /chat endpoint: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'No user query or file provided'}), 400

@app.route("/get_history", methods=["GET"])
def get_history():
    """Lists saved chat sessions sorted by most recent."""
    history = []
    if os.path.exists(SESSIONS_FOLDER):
        for filename in os.listdir(SESSIONS_FOLDER):
            if filename.endswith(".json"):
                base_id = filename.split('.')[0]
                try:
                    chat_id = int(base_id)
                except ValueError:
                    chat_id = base_id
                
                mem = Memory(chat_id, storage_path=SESSIONS_FOLDER)
                title = mem.get_title()
                
                # File modification time for sorting
                fpath = os.path.join(SESSIONS_FOLDER, filename)
                mtime = os.path.getmtime(fpath)
                
                history.append({
                    'id': chat_id,
                    'title': title,
                    'mtime': mtime,
                    'messages_count': len(mem.get_history())
                })
                
    history.sort(key=lambda x: x.get('mtime', 0), reverse=True)
    return jsonify(history)

@app.route("/get_chat/<chat_id>", methods=["GET"])
def get_chat(chat_id):
    """Retrieves full conversation messages for a specific session."""
    memory = Memory(chat_id, storage_path=SESSIONS_FOLDER)
    return jsonify(memory.get_history())

@app.route("/delete_chat/<chat_id>", methods=["POST"])
def delete_chat(chat_id):
    """Deletes a chat session file."""
    try:
        session_file = os.path.join(SESSIONS_FOLDER, f"{chat_id}.json")
        if os.path.exists(session_file):
            os.remove(session_file)
            return jsonify({"status": "success"})
        return jsonify({"error": "Session not found"}), 404
    except Exception as e:
        logger.error(f"Error deleting chat {chat_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route("/clear_history", methods=["POST"])
def clear_history():
    """Clears all session files."""
    try:
        if os.path.exists(SESSIONS_FOLDER):
            for filename in os.listdir(SESSIONS_FOLDER):
                if filename.endswith(".json"):
                    os.remove(os.path.join(SESSIONS_FOLDER, filename))
        return jsonify({"status": "success"})
    except Exception as e:
        logger.error(f"Error clearing history: {e}")
        return jsonify({'error': str(e)}), 500

@app.route("/summarize_research", methods=["GET"])
def summarize_research_route():
    """Direct research API endpoint."""
    try:
        topic = request.args.get("topic", "").strip()
        if not topic:
            return jsonify({"error": "Topic query parameter is required"}), 400
        
        summary, research_papers = summarize_research(topic)
        return jsonify({
            "summary": summary,
            "research_papers": research_papers
        })
    except Exception as e:
        logger.error(f"Error in /summarize_research: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route("/export_chat/<chat_id>", methods=["GET"])
def export_chat(chat_id):
    """Exports conversation session as a formatted Markdown document."""
    memory = Memory(chat_id, storage_path=SESSIONS_FOLDER)
    messages = memory.get_history()
    title = memory.get_title()
    
    md_content = f"# Deep Research Session: {title}\n*Exported on {app.name}*\n\n---\n\n"
    for msg in messages:
        role = msg.get('role', '').capitalize()
        content = msg.get('content')
        if role == 'Context':
            continue
        md_content += f"### {role}\n"
        if isinstance(content, dict):
            md_content += f"{content.get('body', '')}\n\n"
            if content.get('summary'):
                md_content += f"> **Executive Summary**: {content.get('summary')}\n\n"
        else:
            md_content += f"{content}\n\n"
        md_content += "---\n\n"
        
    return Response(
        md_content,
        mimetype="text/markdown",
        headers={"Content-disposition": f"attachment; filename=research_session_{chat_id}.md"}
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    print(f"==================================================")
    print(f"  Deep Research AI Agent running at:")
    print(f"  -> http://127.0.0.1:{port}")
    print(f"==================================================")
    app.run(host="0.0.0.0", port=port, debug=False)
