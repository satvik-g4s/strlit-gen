import streamlit as st
from openai import OpenAI

st.set_page_config(layout="wide")

# --- UI Setup ---
st.title("Pandas to Streamlit Converter")

# API Configuration - Enter your key here or use the sidebar
api_key = st.secrets["api_key"]
model_name = "llama-3.3-70b-versatile" 

# Input Section
col1, col2 = st.columns(2)
with col1:
    pandas_code = st.text_area("Paste your Pandas code here:", height=300, 
                                 placeholder="df = pd.read_csv('data.csv')\nresult = df.groupby('City').sum()")
with col2:
    change_request = st.text_area("Any specific changes? (Optional):", height=300, 
                                    placeholder="e.g. 'Add a chart', 'Use separate uploaders for multiple files', etc.")

if st.button("Generate Streamlit App"):
    if not api_key:
        st.error("Please enter an API key in the sidebar.")
    elif not pandas_code:
        st.warning("Please paste some pandas code first.")
    else:
        try:
            # Initialize Client
            client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=api_key
            )

            # Updated Prompt: Keeping your core rules but adding the functional/descriptive requirement
            system_prompt = """
You are a Python developer.
Convert the given pandas-based CSV code into a simple, professional Streamlit app.

STRICT RULES:
1. Use Streamlit only
2. Always set:
   - st.set_page_config(layout="wide")
   - Light mode only (no styling, no themes, no dark mode)
3. Keep everything minimal and generic

UI REQUIREMENTS:
- File uploader (CSV or xls based on code). If multiple files are in the code, create separate uploaders.
- Single button: "Run"
- Show output only after button click

FUNCTIONAL RULES:
- Use clear function-based structure (e.g., a processing function and a main function).
- File uploader variable name must be `uploaded_file` (or numbered if multiple).
- Read files using pandas.
- Apply the provided pandas operations inside the processing function.
- Display result using st.dataframe().
- Add basic check for file upload.
- No extra features, no text, no explanations.

CODE RULES:
- Single Streamlit file.
- Clean, readable, and descriptive code, No explanatory comments, just add headings in comments.
- No page title, no descriptions, no automation wording.
"""

            # Combine the pandas code with the user's change requests
            user_payload = f"Convert this pandas code:\n\n{pandas_code}"
            if change_request:
                user_payload += f"\n\nADDITIONAL USER REQUESTS/CHANGES: {change_request}"

            with st.spinner("Generating code..."):
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_payload}
                    ],
                    temperature=0.1 
                )

            generated_code = response.choices[0].message.content
            
            # Remove markdown code blocks
            clean_code = generated_code.replace("```python", "").replace("```", "").strip()

            # Output Section
            st.divider()
            st.subheader("Generated Streamlit Code")
            st.code(clean_code, language="python")
            
            # Optional: Download button for the generated file
            st.download_button("Download .py File", clean_code, file_name="app.py", mime="text/x-python")
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
