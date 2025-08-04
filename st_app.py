import streamlit as st
import requests
import json
from PIL import Image
import io

st.set_page_config(page_title="Optimeleon Landing Page Generator", layout="wide", initial_sidebar_state="expanded")

# temp
API_BASE_URL = "http://localhost:8000"

def call_api(endpoint, method="GET", data=None, files=None):
    """Helper function to call FastAPI endpoints"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "POST":
            if files:
                response = requests.post(url, files=files, data=data)
            else:
                response = requests.post(url, json=data)
        else:
            response = requests.get(url)
        
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"API Error: {response.status_code} - {response.text}"
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to API. Make sure FastAPI server is running on localhost:8000"
    except Exception as e:
        return None, f"Error: {str(e)}"

def main():
    st.header('Optimeleon Landing Page Generator')
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('Advertisement Image')
        uploaded_file = st.file_uploader("Upload an advertisement image",type=["jpg", "jpeg", "png", "webp"])
        
        if uploaded_file:
            # showing uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Advertisement", use_container_width=True)
            
            # VLM Image Analysis
            with st.expander("Image Analysis", expanded=True):
                if st.button("Analyze Image"):
                    with st.spinner("Analyzing image..."):
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        analysis_data, analysis_error = call_api("/analyze-image", "POST", files=files)
                        
                        if analysis_error:
                            st.markdown(analysis_error)
                        else:
                            st.session_state['image_analysis'] = analysis_data['image_description']
                            st.write("**Image Analysis:**")
                            st.write(analysis_data['image_description'])
    
    with col2:
        st.markdown('Original Content')
        
        # headline input
        headline = st.text_area(
            "Headline (HTML)",
            height=150,
            value='''<h1 class="font-extrabold text-4xl lg:text-6xl tracking-tight md:-mb-4 flex flex-col">
<span class="relative">Crush Your Personal Best with Nike Vaporfly 3 </span>
<span class="whitespace-nowrap relative ">
<span class="mr-3 sm:mr-4 md:mr-5">Engineered for </span>
<span class="relative whitespace-nowrap">
<span class="absolute bg-neutral-content -left-2 -top-1 -bottom-1 -right-2 md:-left-3 md:-right-3 rotate-1"></span>
<span class="relative text-neutral">Race-Day Speed</span>
</span>
</span>
</h1>'''
        )
        
        # subheadline input
        subheadline = st.text_area(
            "Subheadline",
            height=100,
            value='''<p class="text-lg opacity-80 leading-relaxed">Maximize your race-day potential with cutting-edge energy return, lightweight durability, and a sleek, aerodynamic design that keeps you ahead of the competition.</p>''',
            help="Paste the original subheadline with its HTML structure"
        )
    
    # Marketing Insights
    st.markdown('Marketing Insights')
    marketing_insights = st.text_area(
        "Marketing Insights",
        height=300,
        value="""Product Name: Nike Vaporfly 3 Men's Road Racing Shoes

Product Description: The Nike Vaporfly 3 is a high-performance road racing shoe designed to give runners competitive advantage.

Features and Benefits:
- Race-Day Optimized Performance: Specifically engineered for race-day speed and agility
- Lightweight Yet Durable Design: Lightweight structure with reinforced durability
- Advanced Energy Return System: Innovative sole for maximum energy return
- Versatile for All Levels: Suitable for elite racers and casual runners

Target Audience:
- Elite and Competitive Runners: Desires to break personal records and optimize race-day performance
- Amateur Runners Preparing for Races: Looking to improve performance for significant races
- Fitness Enthusiasts Who Train Regularly: Want advanced technology in their footwear
- Style-Conscious Athletes: Want to look as good as they perform

Pain Points:
- Difficulty finding shoes that maximize speed without compromising comfort
- Challenge of finding balance between comfort, durability, and performance
- Limited selection of stylish running shoes that meet high-performance standards""",
        help="Provide detailed marketing insights about the product, target audience, and pain points"
    )

    # Section for generation of content
    st.markdown('Generate Personalized Content')

    if st.button("Generate Content", use_container_width=True):
            if 'image_analysis' not in st.session_state:
                st.error("Please analyze an image first!")
            else:
                with st.spinner("Generating personalized content..."):
                    data = {
                        "image_description": st.session_state['image_analysis'],
                        "original_headline": headline,
                        "original_subheadline": subheadline,
                        "marketing_insights": marketing_insights
                    }
                    result_data, result_error = call_api("/generate-content", "POST", data=data)
                    if result_error:
                        st.markdown(result_error)
                    else:
                        st.session_state['generated_content'] = result_data
    
    # Results
    if 'generated_content' in st.session_state:
        st.markdown('Generated Results')

        result = st.session_state['generated_content']
        
        # Display image analysis if available
        if 'image_analysis' in result:
            with st.expander("Image Analysis Used"):
                st.write(result['image_analysis'])
        
        custom_html = f"""
        <div style="
            padding: 2rem;
            border-radius: 12px;
            background: linear-gradient(135deg, #ffffff, #f9fafb);
            box-shadow: 0 10px 30px rgba(0,0,0,0.05);
            font-family: 'Helvetica Neue', sans-serif;
        ">
        {result['headline']}
        {result['subheadline']}
        </div>
        """
        st.components.v1.html(custom_html, height=400)

        # JSON output
        st.markdown("**JSON Output:**")
        json_output = {
            "headline": result['headline'],
            "subheadline": result['subheadline']
        }
        st.json(json_output)
        
        # Download
        st.download_button(label="Download as JSON", data=json.dumps(json_output, indent=2), file_name="generated_content.json", mime="application/json")

if __name__ == "__main__":
    main()