import gradio as gr
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
import os
from dotenv import load_dotenv
import random

# Language translations dictionary
TRANSLATIONS = {
    'uz': {
        'title': '📚 Beruniy vorisi AI loyihasi',
        'author_name': 'Nizomiddinov Najmiddin Gʻulomovich',
        'author_title': 'Filologiya va tarix fanlari doktori, professor',
        'project_about': '📘 Loyiha haqida:',
        "project_description": "Ushbu sunʼiy intellekt tizimi akademik Nizomiddinovning Jahoniy sivilizatsiyalar tarixidagi o'zbek davlatchiligi"

                               "kitoblar to'plamiga asoslangan. Savollarni avtomatik tushunadi, matn asosida javob qaytaradi va tarixiy bilimlarni ommalashtirishga xizmat qiladi.",
        'about_scholar': '👤 Olim haqida:',
        'scholar_bio': '''Najmiddin Nizomiddinov 2013-yil «Bobur xalqaro mukofoti» va 2017-yil «Shuhrat medali» bilan mukofotlanib, 2022 yili Oʻzbekiston Fanlar Akademiyasining nishoni bilan taqdirlangan. U Toshkent Davlat universitetining talabasi sifatida 1969-1970 yillari Hindistonning La-khnau universitetida magistrlik boʻyicha tahsil olgach oʻz pedagogik faoliyatini boshlagan.

N.Nizomiddinov 1971-1991 yillar oraligʻida 12 yil Hindiston va Pokiston davlatlarida hind, urdu va ingliz tillari boʻyicha tarjimonlik vazifasini oʻtagan. U "Brahma Kumaris" ruhiy universitetida Raja yoga amaliyoti bilan ham shugʻullangan.

1991 yildan 2007 yilgacha Alisher Navoiy nomidagi Davlat adabiyot muzeyida ilmiy xodim boʻlib ishlagan. 1994 yili filologiya fanlari nomzodi, 2002 yili doktori, 2024 yili esa tarix fanlari boʻyicha ikkinchi doktorlik dissertatsiyasini yoqlagan.

Uning ilmiy ishlari Abu Rayhon Beruniyning "Hindiston" asariga tayangan bo'lib, Osiyo xalqlari tarixi, diniy va dunyoviy qadriyatlarini tahlil qiladi. 75+ maqola, 10+ monografiya, va oʻquv qoʻllanmalar muallifi. Hindiston, Xitoy, Malayziya, Koreya, Yaponiyaga doir ilmiy asarlar yaratgan.

Nizomiddinov tarjimonlik faoliyati doirasida Raj Kapur, Amitabh Bachchan kabi kino yulduzlariga ham xizmat qilgan. Uning "Bu men – Raj Kapur boʻlaman" risolasi hind kino muxlislari orasida mashhur. Olim, shuningdek, sogʻliqni saqlash, yoga va tasavvuf mavzularida ham risolalar yozgan.

U koʻplab xalqaro ilmiy anjumanlar ishtirokchisi, Oʻzbekiston xalqaro islom akademiyasi jamoasining faxriy aʼzosi sifatida tanilgan.
Najmiddin Gʻulomovich Nizomiddinov o'zining ilmiy faoliyatini tarix, adabiyot, va milliy identitet masalalariga bagʻishlagan. Uning asarlari Sharq va Gʻarb uygʻunligi, madaniyatlararo aloqalar va o'zbek davlatchiligi tarixiga bagʻishlangan.''',
        'question_label': '🤔 Savolingizni shu yerga kiriting:',
        'question_placeholder': " Masalan: Rajas guna nima? o'zbek tilida bayon qil?",
        'submit_button': '🧠 Javobni olish',
        'answer_label': '💡 Javob:',
        'examples_label': '💡 Savollar uchun namunalar',
        'books_collection': "📖 Kitoblar to'plami",
        'feedback_title': '🗣 Fikr va takliflaringiz',
        'feedback_description': "Loyiha haqida fikringizni yozing",
        'feedback_label': '✉️ Mulohaza',
        'feedback_placeholder': 'Yozing: sizga nima yoqdi yoki yoqmadi, takliflaringiz...',
        'feedback_button': '📩 Yuborish',
        'language_selector': 'Til / Language',
        'empty_question': 'Iltimos, savolingizni kiriting.',
        'system_error': "Tizimni ishga tushirishda muammo yuz berdi. Iltimos, server loglarini tekshiring va keyinroq urinib ko'ring",
        'query_error_prefix': 'Savolga javob topishda xatolik yuz berdi:',
        'feedback_empty': 'Iltimos, mulohazangizni yozing.',
        'feedback_success': "Fikringiz uchun tashakkur! Yana takliflaringiz bo'lsa,bemalol yozing",
        'examples': [
            "Din fenomenologiyasi nima? o'zbek tilida bayon qil?",
            "Diniy qadriyatlar va tasviriy san'atning inson ma'naviy hayotidagi o'rni qanday?",
            "Sinagoga nima batafsil bayon qil?"
        ]
    },
    'en': {
        'title': '📚 Beruniy Legacy AI Project',
        'author_name': 'Nizomiddinov Najmiddin Gulomovich',
        'author_title': 'Doctor of Philology and History, Professor',
        'project_about': '📘 About the Project:',
        'project_description': 'This artificial intelligence system is based on Academic Nizomiddinov\'s collection of books "Uzbek Statehood in the History of World Civilizations". It automatically understands questions, returns answers based on text, and serves to popularize historical knowledge.',
        'about_scholar': '👤 About the Scholar:',
        'scholar_bio': '''Najmiddin Nizomiddinov was awarded the "Bobur International Award" in 2013 and the "Glory Medal" in 2017, and was honored with the badge of the Academy of Sciences of Uzbekistan in 2022. As a student of Tashkent State University, he studied for a master's degree at Lucknow University in India in 1969-1970, after which he began his pedagogical activity.

N. Nizomiddinov worked as an interpreter in Hindi, Urdu and English languages in India and Pakistan for 12 years from 1971-1991. He also practiced Raja yoga at the "Brahma Kumaris" spiritual university.

From 1991 to 2007, he worked as a researcher at the State Literature Museum named after Alisher Navoi. In 1994 he became a candidate of philological sciences, in 2002 a doctor, and in 2024 he defended his second doctoral dissertation in historical sciences.

His scientific works are based on Abu Rayhan Beruni's work "India" and analyze the history, religious and secular values of Asian peoples. Author of 75+ articles, 10+ monographs, and textbooks. He has created scientific works on India, China, Malaysia, Korea, and Japan.

Within the framework of his translation activities, Nizomiddinov also served film stars such as Raj Kapoor and Amitabh Bachchan. His treatise "This is me - I will be Raj Kapoor" is popular among Indian cinema fans. The scientist has also written treatises on health care, yoga and mysticism.

He is a participant in many international scientific conferences and is known as an honorary member of the International Islamic Academy of Uzbekistan.
Najmiddin Gulomovich Nizomiddinov dedicated his scientific activity to issues of history, literature, and national identity. His works are devoted to the harmony of East and West, intercultural relations and the history of Uzbek statehood.''',
        'question_label': '🤔 Enter your question here:',
        'question_placeholder': ' For example: What is Rajas guna? Explain in Uzbek?',
        'submit_button': '🧠 Get Answer',
        'answer_label': '💡 Answer:',
        'examples_label': '💡 Sample Questions',
        'books_collection': '📖 Book Collection',
        'feedback_title': '🗣 Your Feedback and Suggestions',
        'feedback_description': 'Write your opinion about the project',
        'feedback_label': '✉️ Feedback',
        'feedback_placeholder': 'Write: what you liked or disliked, your suggestions...',
        'feedback_button': '📩 Send',
        'language_selector': 'Language / Til',
        'empty_question': 'Please enter your question.',
        'system_error': 'There was a problem starting the system. Please check the server logs and try again later.',
        'query_error_prefix': 'An error occurred while finding an answer to the question:',
        'feedback_empty': 'Please write your feedback.',
        'feedback_success': 'Thank you for your feedback! Feel free to write more suggestions.',
        'examples': [
            "What is the phenomenology of religion? Explain in Uzbek?",
            "What is the role of religious values and visual arts in human spiritual life?",
            "What is a synagogue? Explain in detail?"
        ]
    }
}

# .env faylidan muhit o'zgaruvchilarni yuklash
load_dotenv()

# Muhit o'zgaruvchilardan API kalitlarini olish
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PINECONE_ENVIRONMENT = os.environ.get("PINECONE_ENVIRONMENT")
INDEX_NAME = "pdf-rag-index"

# OpenAI API kalitini muhit o'zgaruvchilarga qo'shish
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# LlamaIndex Settings konfiguratsiyasi
Settings.llm = OpenAI(model="gpt-3.5-turbo", temperature=0.1)
Settings.embed_model = OpenAIEmbedding(model="text-embedding-ada-002")

# Global o'zgaruvchilar
query_engine = None
pc = None
system_initialized = False
file_path_global = "static/dinshunoslikga_kirish.pdf"
current_language = 'uz'  # Default language


def get_text(key):
    """Get translated text based on current language"""
    return TRANSLATIONS[current_language].get(key, key)


def initialize_system():
    global query_engine, pc, system_initialized

    if system_initialized and query_engine is not None:
        print("💡 Tizim allaqachon ishga tushirilgan.")
        return

    try:
        if not os.path.exists(file_path_global):
            raise FileNotFoundError(f"❌ Fayl topilmadi: {file_path_global}")

        print(f"📄 Fayl topildi: {file_path_global}")

        pc = Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
        existing_indexes = [index.name for index in pc.list_indexes()]

        if INDEX_NAME not in existing_indexes:
            raise ValueError(
                f"❌ Pinecone indeks '{INDEX_NAME}' topilmadi.\n"
                f"👉 Mavjud indekslar: {', '.join(existing_indexes)}\n"
                f"Iltimos, Pinecone'da shu nomdagi indeksni avval yarating."
            )

        print(f"🔗 '{INDEX_NAME}' indeksiga ulanmoqda...")
        vector_store = PineconeVectorStore(pinecone_index=pc.Index(INDEX_NAME))

        print("⏳ PDF fayl o'qilmoqda va indekslanmoqda...")
        documents = SimpleDirectoryReader(input_files=[file_path_global]).load_data()
        index = VectorStoreIndex.from_documents(documents, vector_store=vector_store)

        query_engine = index.as_query_engine(response_mode="tree_summarize", similarity_top_k=5, verbose=True)
        system_initialized = True
        print("✅ Tizim muvaffaqiyatli ishga tushirildi va query engine tayyor!")

    except Exception as e:
        print(f"❌ Tizimni ishga tushirishda xatolik:\n{str(e)}")
        system_initialized = False
        query_engine = None


def query_book(question: str) -> str:
    global query_engine, system_initialized

    if not system_initialized or query_engine is None:
        print("🔄 Tizim hali ishga tushirilmagan yoki xato yuz bergan. Qayta ishga tushirilmoqda...")
        initialize_system()
        if not system_initialized or query_engine is None:
            return f"❌ {get_text('system_error')}"

    if not question.strip():
        return f"❓ {get_text('empty_question')}"

    try:
        print(f"🔍 Savol: {question}")
        response = query_engine.query(question)
        return f"💡 **{get_text('answer_label').replace('💡 ', '')}:**\n\n{str(response)}"
    except Exception as e:
        return f"❌ {get_text('query_error_prefix')} {str(e)}\nIltimos, API kalitlaringiz to'g'ri ekanligiga va Pinecone indeksi faol ekanligiga ishonch hosil qiling."


def collect_feedback(feedback_text):
    if not feedback_text.strip():
        return f"❗️ {get_text('feedback_empty')}"

    with open("feedback_log.txt", "a", encoding="utf-8") as f:
        f.write(feedback_text + "\n---\n")

    return f"✅ {get_text('feedback_success')}"


def change_language(language):
    global current_language
    current_language = language
    return create_interface_components()


def create_interface_components():
    """Create interface with current language"""
    return {
        'title': get_text('title'),
        'author_info': f"""
## {get_text('author_name')}
{get_text('author_title')}

🏅 Bobur xalqaro mukofoti (2013) <br>
🎖 Shuhrat medali (2017) <br>
🧬 Fanlar akademiyasi nishoni (2022)

### {get_text('project_about')}
{get_text('project_description')}

### {get_text('about_scholar')}
{get_text('scholar_bio')}
        """,
        'question_label': get_text('question_label'),
        'question_placeholder': get_text('question_placeholder'),
        'submit_button': get_text('submit_button'),
        'answer_label': get_text('answer_label'),
        'examples_label': get_text('examples_label'),
        'books_collection': get_text('books_collection'),
        'feedback_title': get_text('feedback_title'),
        'feedback_description': get_text('feedback_description'),
        'feedback_label': get_text('feedback_label'),
        'feedback_placeholder': get_text('feedback_placeholder'),
        'feedback_button': get_text('feedback_button'),
        'examples': get_text('examples')
    }


def create_ui():
    with gr.Blocks(css="""
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

        html, body, .gradio-container {
            font-family: 'Inter', sans-serif;
            margin: 0;
            padding: 0;
            background: url("https://i.postimg.cc/pdTWnqzF/background-image.jpg") no-repeat center center fixed;
            background-size: cover;
        }

        /* Faqat matnlar qora rangda */
        p, h1, h2, h3, h4, h5, h6, span, label, li, a {
            color: #000000 !important;
        }

        /* Barcha konteynerlar va elementlar oq */
        div, section, article, aside {
            background-color: transparent;
        }

        /* Input va textarea - oq fon, qora matn */
        input, textarea, select {
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 1px solid #dddddd !important;
            border-radius: 6px !important;
        }

        /* Gradio komponentlari - oq fon */
        .gr-box, .gr-input, .gr-textbox, .gr-form {
            background-color: #ffffff !important;
            border: 1px solid #dddddd !important;
        }

        /* Dropdown - oq fon */
        .gr-dropdown {
            background-color: #ffffff !important;
        }

        /* Placeholder matnlari kulrang */
        input::placeholder, textarea::placeholder {
            color: #666666 !important;
            opacity: 1 !important;
        }

        /* Main container */
        #main-container {
            max-width: 1100px;
            margin: 30px auto;
            padding: 30px;
            background-color: #ffffff !important;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }

        /* Card container */
        .card {
            background-color: #ffffff !important;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            padding: 20px;
            margin-bottom: 24px;
        }

        /* Buttons - faqat buttonlar ko'k */
        .gr-button {
            background-color: #1e88e5 !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600;
            transition: all 0.3s ease-in-out;
        }

        .gr-button:hover {
            transform: scale(1.03);
        }

        /* Book slider */
        #book-slider {
            display: flex;
            overflow-x: auto;
            gap: 20px;
            padding: 15px 0;
            background-color: transparent;
        }

        #book-slider img {
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.2s ease-in-out;
        }

        #book-slider img:hover {
            transform: scale(1.05);
        }

        /* Language selector */
        .language-selector {
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 1000;
            background-color: #ffffff !important;
        }

        /* Accordion */
        .gr-accordion {
            background-color: #ffffff !important;
        }

        /* Examples (Namunalar) section */
        .gr-examples, .gr-samples, .gr-sample-textbox {
            background-color: #ffffff !important;
        }
        .label.svelte-p5q82i.svelte-p5q82i.svelte-p5q82i {
            display: flex;
            align-items: center;
            margin-bottom: var(--size-2);
            color: black;
            font-weight: var(--block-label-text-weight);
            font-size: var(--block-label-text-size);
            line-height: var(--line-sm);
        }

        .gr-examples *, .gr-samples * {
            color: #000000 !important;
        }
        
        .gallery.svelte-1oitfqa {
            padding: var(--size-1) var(--size-2);
            color: black;
        }

        /* Examples table */
        table, th, td, tr {
            color: #000000 !important;
            background-color: #ffffff !important;
        }

        /* Mobile responsive */
        @media (max-width: 768px) {
            #main-container {
                padding: 15px;
            }
            .gr-button {
                width: 100%;
            }
            .language-selector {
                position: relative;
                top: 0;
                right: 0;
                margin-bottom: 20px;
            }
        }
    """) as app:
        # Language selector at the top
        with gr.Row():
            with gr.Column(scale=4):
                pass
            with gr.Column(scale=1):
                language_dropdown = gr.Dropdown(
                    choices=[("O'zbek", "uz"), ("English", "en")],
                    value="uz",
                    label=get_text('language_selector'),
                    elem_classes="language-selector"
                )

        with gr.Column(elem_id="main-container"):
            # Dynamic content that changes with language
            title_md = gr.Markdown(get_text('title'))

            with gr.Row():
                with gr.Column(scale=1):
                    gr.Image("static/nizomiddinov.png", width=250, height=250, show_label=False)
                with gr.Column(scale=3):
                    author_info_md = gr.Markdown(create_interface_components()['author_info'])

            with gr.Column(elem_classes="card"):
                question_input = gr.Textbox(
                    label=get_text('question_label'),
                    placeholder=get_text('question_placeholder'),
                    lines=4
                )
                submit_btn = gr.Button(get_text('submit_button'))
                answer_output = gr.Textbox(
                    label=get_text('answer_label'),
                    lines=6,
                    interactive=False
                )

            # Examples
            examples_component = gr.Examples(
                examples=[[ex] for ex in get_text('examples')],
                inputs=question_input,
                outputs=answer_output,
                fn=query_book,
                label=get_text('examples_label')
            )

            # Books collection
            books_title_md = gr.Markdown(f"### {get_text('books_collection')}")
            with gr.Row(elem_id="book-slider"):
                for i in range(1, 7):
                    gr.Image(f"static/kitob{i}.png", show_label=False, width=160, height=230)

            # Feedback section
            with gr.Accordion(get_text('feedback_title'), open=False):
                with gr.Row():
                    gr.Image("static/feedback.png", width=40, height=40, show_label=False)
                    feedback_desc_md = gr.Markdown(f"### {get_text('feedback_description')}")

                feedback_input = gr.Textbox(
                    label=get_text('feedback_label'),
                    placeholder=get_text('feedback_placeholder'),
                    lines=4
                )
                feedback_button = gr.Button(get_text('feedback_button'))
                feedback_output = gr.Textbox(label="Status", interactive=False)

            # Event handlers
            def on_language_change(lang):
                global current_language
                current_language = lang
                components = create_interface_components()

                return (
                    components['title'],  # title_md
                    components['author_info'],  # author_info_md
                    gr.update(label=components['question_label'], placeholder=components['question_placeholder']),
                    # question_input
                    gr.update(value=components['submit_button']),  # submit_btn
                    gr.update(label=components['answer_label']),  # answer_output
                    f"### {components['books_collection']}",  # books_title_md
                    gr.update(label=components['feedback_label'], placeholder=components['feedback_placeholder']),
                    # feedback_input
                    gr.update(value=components['feedback_button']),  # feedback_button
                    f"### {components['feedback_description']}"  # feedback_desc_md
                )

            language_dropdown.change(
                fn=on_language_change,
                inputs=language_dropdown,
                outputs=[
                    title_md, author_info_md, question_input, submit_btn,
                    answer_output, books_title_md, feedback_input,
                    feedback_button, feedback_desc_md
                ]
            )

            feedback_button.click(fn=collect_feedback, inputs=feedback_input, outputs=feedback_output)
            submit_btn.click(fn=query_book, inputs=question_input, outputs=answer_output)

    return app


# Dasturni ishga tushirish
if __name__ == "__main__":
    print("🌐 Gradio interfeysi ishga tushirilmoqda...")

    # 'static' papkasining mavjudligini tekshirish
    if not os.path.exists("static"):
        os.makedirs("static")
        print("📁 'static' papkasi yaratildi.")

    # Rasmlar mavjudligini tekshirish va foydalanuvchiga eslatma berish
    required_images = ["nizomiddinov.png", "background_image.png"] + [f"kitob{i}.png" for i in range(1, 7)]
    for img_name in required_images:
        if not os.path.exists(os.path.join("static", img_name)):
            print(
                f"⚠️ DIQQAT: 'static/{img_name}' rasmi topilmadi. Iltimos, bu rasmni 'static' papkasiga joylashtiring.")
            print(f"Ilova vizual qismi to'g'ri ko'rinmasligi mumkin.")

    # Tizimni dastlab ishga tushirishga urinish
    initialize_system()

    app = create_ui()
    app.launch(share=True, server_name="0.0.0.0", server_port=8000, quiet=False)
