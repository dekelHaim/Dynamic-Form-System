def get_form_html(form_id: int, form_name: str, description: str, fields_html: str) -> str:
    """Generate complete HTML form"""
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{form_name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f0f2f5; padding: 20px; }}
        .container {{ max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        h1 {{ color: #1a1a1a; margin-bottom: 10px; font-size: 24px; }}
        .description {{ color: #666; font-size: 14px; margin-bottom: 20px; }}
        form {{ display: flex; flex-direction: column; gap: 12px; }}
        input, select {{ padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; font-family: inherit; }}
        input:focus, select:focus {{ outline: none; border-color: #007bff; box-shadow: 0 0 0 3px rgba(0,123,255,0.1); }}
        button {{ padding: 12px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; font-weight: 500; transition: background 0.2s; }}
        button:hover {{ background: #0056b3; }}
        .note {{ color: #999; font-size: 12px; margin-top: 15px; }}
        .loading {{ display: none; color: #007bff; margin-top: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{form_name}</h1>
        {f'<p class="description">{description}</p>' if description else ''}
        
        <form onsubmit="handleSubmit(event)">
            <input type="hidden" name="form_schema_id" value="{form_id}">
            {fields_html}
            <button type="submit">Submit</button>
            <div class="loading" id="loading">Loading...</div>
            <p class="note">* Required fields</p>
        </form>
    </div>
    
    <script>
    async function handleSubmit(e) {{
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const loading = document.getElementById('loading');
        const btn = e.target.querySelector('button');
        
        try {{
            loading.style.display = 'block';
            btn.disabled = true;
            
            const data = Object.fromEntries(formData);
            const res = await fetch('/api/submissions', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{
                    form_schema_id: parseInt(data.form_schema_id),
                    data: Object.fromEntries(Object.entries(data).filter(([k]) => k !== 'form_schema_id')),
                    user_email: data.email || null
                }})
            }});
            
            if (res.ok) {{
                const result = await res.json();
                alert('✅ Submitted! ID: ' + result.id);
                e.target.reset();
            }} else {{
                const err = await res.json();
                const msg = err.detail?.errors?.join(', ') || err.detail;
                alert('❌ Error: ' + msg);
            }}
        }} catch (error) {{
            alert('❌ Error: ' + error.message);
        }} finally {{
            loading.style.display = 'none';
            btn.disabled = false;
        }}
    }}
    </script>
</body>
</html>"""
