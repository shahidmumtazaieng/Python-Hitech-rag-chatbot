const chatflow = {
  "flow_metadata": {
    "flow_name": "HiTech_Professional_Customer_Support_Flow_v3",
    "version": "3.0",
    "company": "Hi-Tech Industrial Group - Saudi Arabia",
    "company_tagline": "Made in Saudi Arabia | Vision 2030 Partner | ISO Certified",
    "tone": "professional_humble_warm",
    "language_support": ["en", "ar"],
    "default_language": "en",
    "api_version": "WhatsApp Business API v18.0",
    "created_date": "2024-11",
    "last_updated": "2024-11",
    "description": "Professional customer support chatflow for Hi-Tech Industrial Group WhatsApp Business API with 7 specialized divisions"
  },
  "webhook_config": {
    "endpoint": "https://your-domain.com/webhook/whatsapp",
    "verify_token": "your_verify_token",
    "port": 3000,
    "events": ["messages", "message_deliveries", "message_reads", "message_template_status_update"]
  },
  "global_settings": {
    "response_delay_ms": 800,
    "typing_indicator": true,
    "session_timeout_minutes": 30,
    "fallback_attempts": 3,
    "human_handoff_keywords": ["agent", "human", "speak", "manager", "supervisor", "complaint", "urgent", "emergency", "help", "support"],
    "response_timeout_seconds": 120,
    "max_retries": 3,
    "analytics_enabled": true,
    "conversation_logger": true
  },
  "business_hours": {
    "saturday": "08:00-18:00",
    "sunday": "08:00-18:00",
    "monday": "08:00-18:00",
    "tuesday": "08:00-18:00",
    "wednesday": "08:00-18:00",
    "thursday": "08:00-18:00",
    "friday": "Close"
  },
  "steps": {
    "welcome": {
      "id": "welcome",
      "type": "interactive_button",
      "message_en": "Assalamu alaikum / Hello! 👋\n\nWelcome to *Hi-Tech Industrial Group* — a proud Saudi manufacturer serving the Kingdom with excellence. 🇸🇦\n\nWe are honored by your visit. Our team is dedicated to providing premium steel solutions, security systems, and smart infrastructure — all proudly *Made in Saudi Arabia* in alignment with Vision 2030.\n\n*How may we serve you today?*\n\nPlease select your language:",
      "message_ar": "السلام عليكم ورحمة الله وبركاته 👋\n\nأهلاً وسهلاً بكم في *مجموعة هي تك الصناعية* — شركة وطنية سعودية تفخر بخدمة الوطن والعملاء. 🇸🇦\n\nنحن ممتنون جداً لزيارتكم. فريقنا ملتزم بتقديم حلول فولاذية عالية الجودة، وأنظمة أمنية، وبنية تحتية ذكية — *صنع في السعودية* وتماشياً مع رؤية 2030.\n\n*كيف يمكننا خدمتكم؟*\n\nيرجى اختيار لغتك:",
      "buttons": [
        { "id": "lang_en", "title_en": "🇬🇧 English", "title_ar": "🇬🇧 English" },
        { "id": "lang_ar", "title_en": "🇸🇦 العربية", "title_ar": "🇸🇦 العربية" }
      ],
      "next": "main_menu",
      "analytics_tag": "session_start"
    },
    "main_menu": {
      "id": "main_menu",
      "type": "interactive_list",
      "header_en": "🏭 Hi-Tech Industrial Group — Main Menu",
      "header_ar": "🏭 مجموعة هي تك الصناعية — القائمة الرئيسية",
      "body_en": "Thank you for connecting with us! We are grateful for the opportunity to serve you.\n\n*Our 7 Specialized Divisions:*\nPlease select the department that interests you. Our team of engineers is ready to assist with technical consultations, custom quotations, project specifications, and after-sales support.",
      "body_ar": "شكراً لتواصلكم معنا! نحن ممتنون لفرصة خدمتكم.\n\n*أقسامنا السبعة المتخصصة:*\nاختروا القسم الذي يهمكم. فريقنا الهندسي جاهز لمساعدتكم في الاستشارات الفنية والعروض المخصصة والمواصفات والدعم ما بعد البيع.",
      "footer_en": "Made in KSA | ISO Certified | Vision 2030 Partner",
      "footer_ar": "صنع في المملكة | معتمدة ISO | شريك رؤية 2030",
      "button_text_en": "📋 View Our Services",
      "button_text_ar": "📋 عرض خدماتنا",
      "sections": [
        {
          "title_en": "🏠 Company Information",
          "title_ar": "🏠 معلومات الشركة",
          "rows": [
            { "id": "menu_about", "title_en": "About Hi-Tech & General Inquiry", "title_ar": "عن هي تك والاستفسارات العامة", "description_en": "Company profile, certifications, video tour" }
          ]
        },
        {
          "title_en": "🛡️ Security & Protection",
          "title_ar": "🛡️ الأمن والحماية",
          "rows": [
            { "id": "menu_fencing", "title_en": "Fencing Solutions", "title_ar": "حلول التسييج" },
            { "id": "menu_barrier", "title_en": "Security Barriers", "title_ar": "حواجز الأمن" }
          ]
        },
        {
          "title_en": "🏗️ Infrastructure & Engineering",
          "title_ar": "🏗️ البنية التحتية والهندسة",
          "rows": [
            { "id": "menu_gabion", "title_en": "Gabion & Erosion Control", "title_ar": "الجبions والتحكم بالتآكل" },
            { "id": "menu_galvanizing", "title_en": "Spin Galvanizing", "title_ar": "التغليف الدوار" }
          ]
        },
        {
          "title_en": "🏢 Building Solutions",
          "title_ar": "🏢 حلول البناء",
          "rows": [
            { "id": "menu_upvc", "title_en": "UPVC Doors & Windows", "title_ar": "أبواب ونوافذ UPVC" },
            { "id": "menu_racks", "title_en": "Racks & Partitions", "title_ar": "الرفوف والفواصل" }
          ]
        },
        {
          "title_en": "🚻 Smart Solutions",
          "title_ar": "🚻 الحلول الذكية",
          "rows": [
            { "id": "menu_smart", "title_en": "Smart Automatic Toilets", "title_ar": "المراحيض الذكية الأوتوماتيكية" }
          ]
        },
        {
          "title_en": "💬 Direct Support",
          "title_ar": "💬 الدعم المباشر",
          "rows": [
            { "id": "menu_speak", "title_en": "Speak to Sales Engineer", "title_ar": "التحدث مع مهندس المبيعات" },
            { "id": "menu_other", "title_en": "Other / Technical Support", "title_ar": "أخرى / الدعم الفني" }
          ]
        }
      ],
      "next_logic": {
        "menu_about": "about_submenu",
        "menu_fencing": "fencing_submenu",
        "menu_gabion": "gabion_submenu",
        "menu_upvc": "upvc_submenu",
        "menu_barrier": "barrier_submenu",
        "menu_galvanizing": "galvanizing_submenu",
        "menu_racks": "racks_submenu",
        "menu_smart": "smart_submenu",
        "menu_speak": "speak_engineer",
        "menu_other": "other_support"
      }
    },
    "about_submenu": {
      "id": "about_submenu",
      "type": "interactive_button",
      "header_en": "About Hi-Tech Industrial Group",
      "header_ar": "عن مجموعة هي تك الصناعية",
      "body_en": "We are a *Saudi-owned and operated* industrial group headquartered in Riyadh.\n\n*Our Legacy:*\n• Premium steel-based industrial solutions\n• 7 specialized verticals under one umbrella\n• ISO 9001 certified manufacturing\n• Vision 2030 aligned & locally manufactured\n• Serving Oil & Gas, Infrastructure, Government & Private sectors\n\n*How may we assist you today?*",
      "body_ar": "نحن مجموعة صناعية *سعودية 100%* مقرها الرياض.\n\n*إرثنا:*\n• حلول صناعية فولاذية عالية الجودة\n• 7 أقسام متخصصة تحت مظلة واحدة\n• تصنيع معتمد ISO 9001\n• متوافقة مع رؤية 2030 ومصنعة محلياً\n• نخدم قطاعات النفط والبنية التحتية والحكومة\n\n*كيف يمكننا مساعدتكم؟*",
      "buttons": [
        { "id": "about_profile", "title_en": "📄 Company Profile", "title_ar": "📄 نبذة الشركة" },
        { "id": "about_video", "title_en": "🎥 Factory Video Tour", "title_ar": "🎥 جولة المصنع" },
        { "id": "about_brochure", "title_en": "📥 Download Brochure", "title_ar": "📥 تحميل الكتيب" },
        { "id": "about_question", "title_en": "❓ General Inquiry", "title_ar": "❓ استفسار عام" }
      ],
      "next_logic": {
        "about_profile": "send_document",
        "about_video": "send_video",
        "about_brochure": "send_document",
        "about_question": "general_inquiry_form"
      }
    },
    "fencing_submenu": {
      "id": "fencing_submenu",
      "type": "interactive_list",
      "header_en": "🛡️ Fencing Solutions",
      "header_ar": "🛡️ حلول التسييج",
      "body_en": "Thank you for your interest in our *HCIS & Aramco-compliant* fencing solutions.\n\n*Our Expertise:*\n• Perimeter security for critical infrastructure\n• Residential & commercial compounds\n• Industrial facilities & construction sites\n• HCIS & Aramco certified solutions\n\n*Please select your requirement:*",
      "body_ar": "شكراً لاهتمامكم بحلول التسييج *المتوافقة مع أرامكو وهيس*.\n\n*خبراتنا:*\n• أمن المحيط للبنية التحتية الحيوية\n• مجمعات سكنية وتجارية\n• منشآت صناعية ومواقع بناء\n• حلول معتمدة من أرامكو وهيس\n\n*اختر احتياجاتك:*",
      "button_text_en": "Select Fence Type",
      "button_text_ar": "اختيار نوع السياج",
      "rows": [
        { "id": "fence_chainlink", "title_en": "Chain Link Fence", "title_ar": "السياج الشبكي" },
        { "id": "fence_welded", "title_en": "Welded Mesh Fence", "title_ar": "السياج الملحوم" },
        { "id": "fence_security", "title_en": "Security Mesh (Anti-Climb)", "title_ar": "الشبك الأمني" },
        { "id": "fence_swing", "title_en": "Swing Gates", "title_ar": "البوابات الدوارة" },
        { "id": "fence_sliding", "title_en": "Sliding Gates", "title_ar": "البوابات المنزلقة" },
        { "id": "fence_heras", "title_en": "Heras Temporary Fencing", "title_ar": "سياج هيراس المؤقت" }
      ],
      "next": "fencing_deep_dive"
    },
    "fencing_deep_dive": {
      "id": "fencing_deep_dive",
      "type": "interactive_button",
      "body_en": "Excellent choice! To provide the most accurate technical solution and quotation, please help us with a few details:\n\n*Key Questions:*\n• Project location (city/region)?\n• Perimeter length (approx. meters)?\n• Security level required (standard/high/maximum)?\n• Ground conditions (flat/rocky/sandy)?\n• Need gate automation?\n\n*How would you like to proceed?*",
      "body_ar": "اختيار ممتاز! لتقديم الحل التقني الدقيق، ساعدونا بتفاصيل قليلة:\n\n*الأسئلة الرئيسية:*\n• موقع المشروع (المدينة/المنطقة)؟\n• طول المحيط (بالأمتار)؟\n• مستوى الأمن المطلوب؟\n• حالة الأرض (مسطحة/صخرية/رملية)؟\n• هل تحتاج لأتمتة البوابات؟\n\n*كيف تود المتابعة؟*",
      "buttons": [
        { "id": "fence_quote", "title_en": "📋 Request Detailed Quote", "title_ar": "📋 طلب عرض سعر" },
        { "id": "fence_specs", "title_en": "📊 Technical Specs", "title_ar": "📊 المواصفات الفنية" },
        { "id": "fence_gallery", "title_en": "📸 Project Gallery", "title_ar": "📸 معرض المشاريع" },
        { "id": "fence_engineer", "title_en": "👨‍🔧 Speak to Engineer", "title_ar": "👨‍🔧 استشارة مهندس" }
      ],
      "next_logic": {
        "fence_quote": "fencing_quotation_form",
        "fence_specs": "send_document",
        "fence_gallery": "send_document",
        "fence_engineer": "speak_engineer"
      }
    },
    "fencing_quotation_form": {
      "id": "fencing_quotation_form",
      "type": "text",
      "header_en": "Fencing Project Quotation Form",
      "header_ar": "نموذج عرض سعر مشروع التسييج",
      "body_en": "We are honored to prepare a customized quotation for your fencing project.\n\n*Please provide the following details:*\n\n1️⃣ *Project Location:* City/Region in KSA\n2️⃣ *Site Type:* Industrial/Residential/Commercial/Aramco/Oil & Gas\n3️⃣ *Perimeter Length:* Approximate linear meters\n4️⃣ *Fence Height Required:* 1.5m / 2.0m / 2.4m / 3.0m / Other\n5️⃣ *Security Level:* Standard / High / Maximum (anti-climb)\n6️⃣ *Ground Condition:* Flat / Sloped / Rocky / Sandy\n7️⃣ *Gate Requirements:* Number and type (swing/sliding/automated)\n8️⃣ *Timeline:* When do you need installation?\n9️⃣ *Budget Range:* Optional\n\n*You may also upload:*\n• Site drawings or maps\n• Photos of the area\n• BOQ (Bill of Quantities)\n\nOur engineering team will respond within *2-4 working hours* with a comprehensive proposal, In sha Allah.",
      "body_ar": "نتشرف بإعداد عرض سعر مخصص لمشروع التسييج الخاص بكم.\n\n*يرجى تزويدنا بالتفاصيل التالية:*\n\n1️⃣ *موقع المشروع:* المدينة/المنطقة\n2️⃣ *نوع الموقع:* صناعي/سكني/تجاري/أرامكو/نفط وغاز\n3️⃣ *طول المحيط:* بالأمتار الخطية\n4️⃣ *ارتفاع السياج المطلوب:* 1.5م / 2.0م / 2.4م / 3.0م / أخرى\n5️⃣ *مستوى الأمن:* عادي / عالي / أقصى (مضاد للتسلق)\n6️⃣ *حالة الأرض:* مسطحة / مائلة / صخرية / رملية\n7️⃣ *متطلبات البوابات:* العدد والنوع (دوارة/منزلقة/أوتوماتيكية)\n8️⃣ *الجدول الزمني:* متى تحتاج الانتهاء؟\n9️⃣ *نطاق الميزانية:* اختياري\n\n*يمكن أيضاً رفع:*\n• رسومات أو خرائط الموقع\n• صور للمنطقة\n• جدول الكميات\n\nسيقوم فريقنا الهندسي بالرد خلال *2-4 ساعات عمل* بعرض شامل، إن شاء الله.",
      "requires_human_followup": true,
      "next": "quote_submitted"
    },
    "gabion_submenu": {
      "id": "gabion_submenu",
      "type": "interactive_list",
      "header_en": "🪨 Gabion & Erosion Control Solutions",
      "header_ar": "🪨 حلول الجبions والتحكم بالتآكل",
      "body_en": "Thank you for considering our *ASTM-certified* gabion solutions.\n\n*Applications:*\n• Retaining walls & slope stabilization\n• Riverbank & coastal protection\n• Landscaping & architectural features\n• Military/defense barriers\n• Flood control systems\n\n*Select your application:*",
      "body_ar": "شكراً لاهتمامكم بحلول الجبions *المعتمدة ASTM*.\n\n*التطبيقات:*\n• جدران الاستناد وتثبيت المنحدرات\n• حماية ضفاف الأنهار والسواحل\n• المناظر الطبيعية والعناصر المعمارية\n• الحواجز العسكرية/الدفاعية\n• أنظمة السيطرة على الفيضانات\n\n*اختر التطبيق:*",
      "rows": [
        { "id": "gabion_retaining", "title_en": "Retaining Walls", "title_ar": "جدران الاستناد" },
        { "id": "gabion_erosion", "title_en": "River/Coastal Protection", "title_ar": "حماية الأنهار/السواحل" },
        { "id": "gabion_landscape", "title_en": "Landscaping & Architecture", "title_ar": "المناظر الطبيعية" },
        { "id": "gabion_military", "title_en": "Military/Defense Barriers", "title_ar": "حواجز عسكرية" },
        { "id": "gabion_flood", "title_en": "Flood Control", "title_ar": "السيطرة على الفيضانات" }
      ],
      "next": "gabion_deep_dive"
    },
    "gabion_deep_dive": {
      "id": "gabion_deep_dive",
      "type": "interactive_button",
      "body_en": "We appreciate your interest in our gabion systems. To engineer the optimal solution, please tell us:\n\n*Technical Details:*\n• Wall height and length required?\n• Soil type (clay/sand/rock)?\n• Water exposure (seasonal/permanent/none)?\n• Load requirements?\n• Aesthetic requirements (natural stone/facing)?\n\n*Our engineers will recommend:*\n• Gabion type (woven/welded)\n• Mesh specifications\n• Filling material\n• Installation methodology",
      "body_ar": "نقدر اهتمامكم بأنظمة الجبions. لتصميم الحل الأمثل:\n\n*التفاصيل الفنية:*\n• ارتفاع وطول الجدار؟\n• نوع التربة (طينية/رملية/صخرية)؟\n• التعرض للمياه (موسمي/دائم/لا)؟\n• متطلبات الأحمال؟\n• المتطلبات الجمالية (حجر/واجهة)؟\n\n*سيوصي مهندسونا بـ:*\n• نوع الجبion (منسوج/ملحوم)\n• مواصفات الشبك\n• مواد الحشو\n• منهجية التركيب",
      "buttons": [
        { "id": "gabion_quote", "title_en": "Request Technical Quote", "title_ar": "طلب عرض سعر تقني" },
        { "id": "gabion_calc", "title_en": "Volume Calculator", "title_ar": "حاسبة الحجم" },
        { "id": "gabion_support", "title_en": "Speak to Engineer", "title_ar": "استشارة مهندس" }
      ],
      "next_logic": {
        "gabion_quote": "gabion_quotation_form",
        "gabion_calc": "send_document",
        "gabion_support": "speak_engineer"
      }
    },
    "gabion_quotation_form": {
      "id": "gabion_quotation_form",
      "type": "text",
      "header_en": "Gabion Project Quotation Form",
      "header_ar": "نموذج عرض سعر مشروع الجبions",
      "body_en": "We are pleased to prepare a comprehensive gabion solution proposal.\n\n*Project Information Required:*\n\n📍 *Site Location:* City/Region\n🏗️ *Project Type:* Infrastructure / Commercial / Residential / Military / Landscaping\n\n📏 *Dimensions:*\n   • Wall height (meters)\n   • Wall length (meters)\n   • Base width if known\n\n🌍 *Site Conditions:*\n   • Soil bearing capacity (if known)\n   • Ground water level\n   • Slope angle (if applicable)\n\n💧 *Hydraulic Conditions:*\n   • River flow rate (for river works)\n   • Wave height (for coastal)\n   • Rainfall intensity (for drainage)\n\n🎨 *Aesthetic Requirements:*\n   • Stone type preference\n   • Need for architectural facing?\n\n📋 *Documentation Available:*\n   • Topographical survey\n   • Geotechnical report\n   • Architectural drawings\n\n*Our response will include:*\n• Detailed BOQ\n• Installation methodology\n• Project timeline\n• Warranty terms",
      "body_ar": "يسعدنا إعداد اقتراح شامل لحل الجبions.\n\n*المعلومات المطلوبة للمشروع:*\n\n📍 *موقع الموقع:* المدينة/المنطقة\n🏗️ *نوع المشروع:* بنية تحتية / تجاري / سكني / عسكري / مناظر طبيعية\n\n📏 *الأبعاد:*\n   • ارتفاع الجدار (أمتار)\n   • طول الجدار (أمتار)\n   • عرض القاعدة إن وُجد\n\n🌍 *ظروف الموقع:*\n   • قدرة تحمل التربة\n   • منسوب المياه الجوفية\n   • زاوية الميل\n\n💧 *الظروف الهيدروليكية:*\n   • معدل تدفق النهر\n   • ارتفاع الأمواج\n   • شدة الأمطار\n\n🎨 *المتطلبات الجمالية:*\n   • تفضيل نوع الحجر\n   • واجهة معمارية؟\n\n📋 *المستندات المتوفرة:*\n   • مساحة طبوغرافية\n   • تقرير جيوتقني\n   • رسومات معمارية",
      "requires_human_followup": true,
      "next": "quote_submitted"
    },
    "upvc_submenu": {
      "id": "upvc_submenu",
      "type": "interactive_list",
      "header_en": "🚪 UPVC Doors & Windows (Maskni Brand)",
      "header_ar": "🚪 أبواب ونوافذ UPVC (Maskni)",
      "body_en": "Welcome to *Maskni* — our premium UPVC brand designed for the Saudi climate.\n\n*Key Benefits:*\n• Thermal insulation (reduce AC costs up to 30%)\n• Sound insulation (40dB reduction)\n• Dust & sand storm resistant\n• No painting or maintenance\n• 10+ years warranty\n\n*What interests you?*",
      "body_ar": "أهلاً بكم في *Maskni* — علامتنا الممتازة للـ UPVC.\n\n*الفوائد الرئيسية:*\n• عزل حراري (توفير حتى 30%)\n• عزل صوتي (40 ديسيبل)\n• مقاوم للغبار والعواصف\n• لا يحتاج صيانة\n• ضمان أكثر من 10 سنوات\n\n*ما يهمك؟*",
      "rows": [
        { "id": "upvc_window", "title_en": "UPVC Windows", "title_ar": "نوافذ UPVC" },
        { "id": "upvc_door", "title_en": "UPVC Doors", "title_ar": "أبواب UPVC" },
        { "id": "upvc_wpc", "title_en": "WPC Doors", "title_ar": "أبواب WPC" },
        { "id": "upvc_facade", "title_en": "Full Façade Solutions", "title_ar": "حلول الواجهات" }
      ],
      "next": "upvc_deep_dive"
    },
    "upvc_deep_dive": {
      "id": "upvc_deep_dive",
      "type": "interactive_button",
      "body_en": "Excellent choice for energy efficiency! To recommend the perfect solution, please help us understand:\n\n*Project Assessment:*\n• Building type (villa/apartment/commercial)?\n• Number of openings needed?\n• Preferred opening style (sliding/casement/fixed)?\n• Color preference (white/wood grain/custom)?\n• Glass type (single/double/tempered/Low-E)?\n• Security level (standard/reinforced/multi-point)?\n\n*We offer free site measurement and consultation in:*\nRiyadh, Jeddah, Dammam, and surrounding areas.",
      "body_ar": "اختيار ممتاز لكفاءة الطاقة!\n\n*تقييم المشروع:*\n• نوع المبنى (فيلا/شقة/تجاري)؟\n• عدد الفتحات؟\n• نمط الفتح المفضل؟\n• تفضيل اللون؟\n• نوع الزجاج؟\n• مستوى الأمن؟\n\n*نقدم قياس واستشارة مجانية في:*\nالرياض، جدة، الدمام",
      "buttons": [
        { "id": "upvc_quote", "title_en": "Request Free Quote", "title_ar": "طلب عرض سعر" },
        { "id": "upvc_visit", "title_en": "Schedule Site Visit", "title_ar": "جدولة زيارة" },
        { "id": "upvc_catalog", "title_en": "Download Catalog", "title_ar": "تحميل الكتالوج" }
      ],
      "next_logic": {
        "upvc_quote": "upvc_quotation_form",
        "upvc_visit": "schedule_visit_form",
        "upvc_catalog": "send_document"
      }
    },
    "upvc_quotation_form": {
      "id": "upvc_quotation_form",
      "type": "text",
      "header_en": "Maskni UPVC Quotation Form",
      "header_ar": "نموذج عرض سعر Maskni UPVC",
      "body_en": "We are delighted to prepare your Maskni UPVC quotation.\n\n*Please share the following details:*\n\n🏠 *Project Information:*\n• Property type: Villa / Apartment / Commercial / Hospital / School\n• Location: City / District\n• Construction phase: Planning / Under construction / Renovation\n\n🪟 *Window/Door Requirements:*\n• Number of windows and approx. sizes (width x height cm)\n• Number of doors and types (main/balcony/bathroom)\n• Preferred profile series (60mm/70mm/80mm)\n• Opening mechanism: Sliding / Casement / Tilt & Turn / Fixed\n\n🎨 *Finishing Preferences:*\n• Color: White / Beige / Wood grain (Oak/Walnut/Mahogany)\n• Glass: Clear / Frosted / Tempered / Double / Low-E\n• Hardware: Standard / Premium (German)\n• Screens: Mosquito nets required?\n\n📅 *Timeline:* When do you need installation?\n💰 *Budget:* Economy / Standard / Premium\n\n*Optional:* Upload architectural drawings or photos.",
      "body_ar": "يسعدنا إعداد عرض سعر Maskni UPVC.\n\n*يرجى مشاركة:*\n\n🏠 *معلومات المشروع:*\n• نوع العقار: فيلا / شقة / تجاري / مستشفى / مدرسة\n• الموقع: المدينة / الحي\n• مرحلة البناء: تخطيط / تحت الإنشاء / تجديد\n\n🪟 *متطلبات النوافذ/الأبواب:*\n• عدد النوافذ والأحجام (العرض × الارتفاع بالسم)\n• عدد الأبواب والأنواع (رئيسية/بلكونة/حمام)\n• سلسلة البروفيل المفضلة (60مم/70مم/80مم)\n• آلية الفتح: منزلقة / شباك / ميل ودوران / ثابتة\n\n🎨 *تفضيلات التشطيب:*\n• اللون: أبيض / بيج / حبوب خشب\n• الزجاج: شفاف / متجمد / مقسى / مزدوج / منخفض\n• الأجهزة: عادي / ممتاز (ألماني)\n• الشبكات: ناموس؟\n\n📅 *الجدول الزمني:* متى؟\n💰 *الميزانية:* اقتصادي / قياسي / ممتاز",
      "requires_human_followup": true,
      "next": "quote_submitted"
    },
    "barrier_submenu": {
      "id": "barrier_submenu",
      "type": "interactive_list",
      "header_en": "🚧 Security Barriers & Access Control",
      "header_ar": "🚧 حواجز الأمن والتحكم بالدخول",
      "body_en": "Thank you for trusting us with your access control requirements.\n\n*Our Solutions:*\n• Automatic boom barriers (parking/roads)\n• Smart solar-powered gates (Parklio)\n• Pedestrian control barriers\n• High-security crash-rated barriers\n• Advertising barriers\n\n*Select your application:*",
      "body_ar": "شكراً لثقتكم بنا.\n\n*حلولنا:*\n• حواجز بوابات أوتوماتيكية\n• بوابات ذكية شمسية (Parklio)\n• حواجز المشاة\n• حواجز أمنية عالية\n• حواجز إعلانية\n\n*اختر التطبيق:*",
      "rows": [
        { "id": "barrier_boom", "title_en": "Automatic Boom Barriers", "title_ar": "حواجز البوابات الأوتوماتيكية" },
        { "id": "barrier_parklio", "title_en": "Smart Solar Gates (Parklio)", "title_ar": "بوابات ذكية شمسية" },
        { "id": "barrier_pedestrian", "title_en": "Pedestrian Barriers", "title_ar": "حواجز المشاة" },
        { "id": "barrier_advertising", "title_en": "Advertising Barriers", "title_ar": "حواجز إعلانية" },
        { "id": "barrier_crash", "title_en": "High-Security Crash Barriers", "title_ar": "حواجز عالية الأمن" },
        { "id": "barrier_faac", "title_en": "FAAC Heavy-Duty Barriers", "title_ar": "حواجز FAAC الثقيلة" }
      ],
      "next": "barrier_deep_dive"
    },
    "barrier_deep_dive": {
      "id": "barrier_deep_dive",
      "type": "interactive_button",
      "body_en": "To recommend the optimal barrier solution, we need to understand your traffic and security:\n\n*Critical Questions:*\n• Vehicle type (cars/trucks/buses/heavy equipment)?\n• Traffic frequency (vehicles per hour, peak)?\n• Power availability (solar/electric/hybrid)?\n• Integration needs (RFID/ANPR/intercom)?\n• Crash rating required (K4/K8/K12)?\n• Opening speed requirements?",
      "body_ar": "لنوصي بحل الحاجز الأمثل:\n\n*أسئلة حاسمة:*\n• نوع المركبات (سيارات/شاحنات/حافلات/معدات)؟\n• تردد الحركة (مركبات في الساعة)؟\n• توفر الكهرباء (شمسي/كهربائي/هجين)؟\n• احتياجات التكامل (RFID/ANPR/اتصال)؟\n• تصنيف الاصطدام (K4/K8/K12)؟\n• سرعة الفتح؟",
      "buttons": [
        { "id": "barrier_quote", "title_en": "Request Quote", "title_ar": "طلب عرض سعر" },
        { "id": "barrier_specs", "title_en": "Technical Data", "title_ar": "البيانات الفنية" }
      ],
      "next_logic": {
        "barrier_quote": "barrier_quotation_form",
        "barrier_specs": "send_document"
      }
    },
    "barrier_quotation_form": {
      "id": "barrier_quotation_form",
      "type": "text",
      "header_en": "Access Control Solution Form",
      "header_ar": "نموذج حل التحكم بالدخول",
      "body_en": "We are ready to engineer your access control solution.\n\n*Site & Traffic Analysis:*\n\n🚗 *Vehicle Profile:*\n• Types: Cars only / Mixed / Heavy trucks / Buses\n• Frequency: ___ vehicles per hour (peak)\n• Direction: One-way / Two-way / Multiple lanes\n\n⚡ *Power & Environment:*\n• Power source available? Yes / No (solar preferred)\n• Outdoor conditions: Normal / Coastal / Desert\n• Temperature range expected\n\n🔐 *Security Level:*\n• Standard (parking management)\n• High (corporate/government)\n• Maximum (critical infrastructure, K4/K8/K12)\n\n📡 *Integration Requirements:*\n• Access control: RFID / Biometric / ANPR\n• Visitor management: Intercom / QR codes / Mobile app\n• Central monitoring: CCTV / Remote management\n\n📍 *Installation Site:*\n• Address / GPS coordinates\n• Road width / Lane configuration\n• Existing foundation or new\n\n⏰ *Timeline:* Urgent / Standard / Future",
      "body_ar": "نحن مستعدون لهندسة حل التحكم بالدخول.\n\n*تحليل الموقع والحركة:*\n\n🚗 *ملف المركبات:*\n• الأنواع: سيارات فقط / مختلطة / شاحنات / حافلات\n• التردد: ___ مركبة (ذروة)\n• الاتجاه: اتجاه واحد / اتجاهان / مسارات\n\n⚡ *الطاقة والبيئة:*\n• الكهرباء متوفرة؟ نعم / لا (شمسي مفضل)\n• الظروف: عادية / ساحلية / صحراوية\n• نطاق درجات الحرارة\n\n🔐 *مستوى الأمن:*\n• قياسي (مواقف)\n• عالي (شركات/حكومة)\n• أقصى (بنية حيوية)\n\n📡 *متطلبات التكامل:*\n• التحكم: RFID / بيومتري / ANPR\n• إدارة الزوار: اتصال / QR / تطبيق\n• المراقبة: CCTV / إدارة عن بعد\n\n📍 *موقع التركيب:*\n• العنوان / GPS\n• عرض الطريق\n• أساس موجود أو جديد\n\n⏰ *الجدول الزمني:* عاجل / قياسي / مستقبلي",
      "requires_human_followup": true,
      "next": "quote_submitted"
    },
    "galvanizing_submenu": {
      "id": "galvanizing_submenu",
      "type": "interactive_list",
      "header_en": "⚙️ Spin Galvanizing & Steel Basics",
      "header_ar": "⚙️ التغليف الدوار وأساسيات الصلب",
      "body_en": "Welcome to the *first dedicated small-parts spin-galvanizing line in KSA*.\n\n*Our Specialization:*\n• Parts under 3kg only\n• Thread-safe galvanizing\n• 24-48 hour turnaround\n• ASTM A123/A153 compliant\n• ISO 9001 certified\n\n*What type of parts do you need galvanized?*",
      "body_ar": "أهلاً بكم في *أول خط متخصص للتغليف الدوار في المملكة*.\n\n*تخصصنا:*\n• قطع أقل من 3 كجم\n• تغليف آمن للخيوط\n• وقت 24-48 ساعة\n• متوافق ASTM A123/A153\n• معتمد ISO 9001\n\n*ما نوع القطع التي تحتاج؟*",
      "rows": [
        { "id": "galv_fasteners", "title_en": "Bolts, Nuts & Fasteners", "title_ar": "المسامير والصواميل" },
        { "id": "galv_clamps", "title_en": "Clamps, Mounts & Brackets", "title_ar": "المشابك والحوامل" },
        { "id": "galv_electrical", "title_en": "Electrical & Cable Accessories", "title_ar": "ملحقات الكهرباء" },
        { "id": "galv_solar", "title_en": "Solar Mounting Hardware", "title_ar": "أجهزة تركيب الطاقة" },
        { "id": "galv_custom", "title_en": "Custom Small Parts", "title_ar": "قطع صغيرة مخصصة" },
        { "id": "galv_bulk", "title_en": "Bulk Processing Quote", "title_ar": "معالجة بالجملة" }
      ],
      "next": "galvanizing_deep_dive"
    },
    "galvanizing_deep_dive": {
      "id": "galvanizing_deep_dive",
      "type": "interactive_button",
      "body_en": "We understand the critical importance of corrosion protection for your steel components.\n\n*Our Process Advantages:*\n• Centrifugal spinning ensures uniform coating\n• Thread protection technology (no re-tapping needed)\n• Fast turnaround for urgent projects\n• Pickling and surface prep included\n• Coating thickness testing reports\n\n*To provide accurate pricing, please tell us:*\n• Total weight or piece count?\n• Part dimensions (max L×W×H)?\n• Current finish (black/painted/pre-galv)?\n• Required coating thickness?",
      "body_ar": "نحن نفهم أهمية الحماية من التآكل.\n\n*مميزات عمليتنا:*\n• دوران طردي موحد\n• حماية الخيوط\n• تنفيذ سريع\n• التنقية مشمولة\n• تقارير الاختبار\n\n*لتسعير دقيق:*\n• الوزن الإجمالي أو العدد؟\n• أبعاد القطع (أقصى)؟\n• التشطيب الحالي؟\n• سماكة الطلاء المطلوبة؟",
      "buttons": [
        { "id": "galv_upload", "title_en": "📎 Upload Parts/Drawings", "title_ar": "📎 رفع قائمة القطع" },
        { "id": "galv_quote", "title_en": "💰 Request Pricing", "title_ar": "💰 طلب التسعير" },
        { "id": "galv_process", "title_en": "🔬 Process Details", "title_ar": "🔬 تفاصيل العملية" }
      ],
      "next_logic": {
        "galv_upload": "galvanizing_quotation_form",
        "galv_quote": "galvanizing_quotation_form",
        "galv_process": "send_document"
      }
    },
    "galvanizing_quotation_form": {
      "id": "galvanizing_quotation_form",
      "type": "text",
      "header_en": "Spin Galvanizing Quotation Form",
      "header_ar": "نموذج عرض سعر التغليف الدوار",
      "body_en": "We are pleased to quote your spin galvanizing requirements.\n\n*Part Details Required:*\n\n📋 *Item Description:*\n• Part name and function\n• Material: Mild steel / High tensile / Cast iron\n• Current condition: Black / Painted / Rusty / Pre-galv\n\n📏 *Dimensions & Weight:*\n• Quantity of pieces\n• Max dimensions per piece (L×W×H mm)\n• Weight per piece or total batch\n• Hollow sections or closed cavities?\n\n🔩 *Thread/Specification Details:*\n• Thread size and pitch\n• Tolerance requirements\n• Critical dimensions\n• Standards: ASTM A123 / A153 / A767\n\n📊 *Coating Requirements:*\n• Coating thickness: Standard (50-75μm) / Heavy (75-100μm)\n• Appearance: Bright / Matte / Passivated\n\n🚚 *Logistics:*\n• Pickup required?\n• Delivery location:\n• Urgency: Standard (48hr) / Express (24hr)\n\n*Please upload:*\n• Photos of parts\n• Technical drawings (PDF/DWG)\n• Excel list with quantities",
      "body_ar": "يسعدنا تقديم عرض سعر للتغليف الدوار.\n\n*تفاصيل القطع:*\n\n📋 *وصف القطعة:*\n• الاسم والوظيفة\n• المادة: فولاذ معتدل / عالي الشد / حديد زهر\n• الحالة: أسود / مطلي / صدأ / مغلف مسبقاً\n\n📏 *الأبعاد والوزن:*\n• عدد القطع\n• الأبعاد القصوى (ط×ع×ا بالمم)\n• وزن القطعة أو الدفعة\n• أقسام مجوفة أو تجاويف؟\n\n🔩 *تفاصيل الخيوط:*\n• حجم ودرجة الخيط\n• متطلبات التسامح\n• الأبعاد الحرجة\n• المعايير: ASTM A123 / A153 / A767\n\n📊 *متطلبات الطلاء:*\n• السماكة: قياسي (50-75) / ثقيل (75-100)\n• المظهر: لامع / مطفي / معالج\n\n🚚 *اللوجستيات:*\n• استلام؟\n• موقع التسليم:\n• السرعة: قياسي (48) / سريع (24)\n\n*رفع:*\n• صور\n• رسومات\n• قائمة Excel",
      "requires_human_followup": true,
      "next": "quote_submitted"
    },
    "racks_submenu": {
      "id": "racks_submenu",
      "type": "interactive_list",
      "header_en": "📦 Racks, Shelving & Partitions",
      "header_ar": "📦 الرفوف والأرفف والفواصل",
      "body_en": "Thank you for your interest in our *Made in KSA* storage solutions.\n\n*Manufacturing Capabilities:*\n• Heavy-duty pallet racking\n• Medium-duty warehouse shelving\n• Office partitions and cubicles\n• Retail display systems\n• Custom fabrication\n\n*What storage challenge can we solve?*",
      "body_ar": "شكراً لاهتمامكم بحلول التخزين *المصنعة في المملكة*.\n\n*القدرات التصنيعية:*\n• رفوف pallets الثقيلة\n• أرفف المستودعات\n• فواصل المكاتب\n• أنظمة العرض\n• تصنيع مخصص\n\n*ما التحدي التخزيني؟*",
      "rows": [
        { "id": "rack_pallet", "title_en": "Heavy-Duty Pallet Racking", "title_ar": "رفوف pallets الثقيلة" },
        { "id": "rack_shelving", "title_en": "Industrial Shelving", "title_ar": "الأرفف الصناعية" },
        { "id": "rack_office", "title_en": "Office Partitions", "title_ar": "فواصل المكاتب" },
        { "id": "rack_retail", "title_en": "Retail & Display", "title_ar": "أنظمة التجزئة" },
        { "id": "rack_mezzanine", "title_en": "Mezzanine Floors", "title_ar": "الأرضيات المتوسطة" }
      ],
      "next": "racks_deep_dive"
    },
    "racks_deep_dive": {
      "id": "racks_deep_dive",
      "type": "interactive_button",
      "body_en": "We design storage systems that maximize space efficiency and safety.\n\n*Engineering Considerations:*\n• Load capacity per level?\n• Product dimensions (L×W×H) and weight?\n• Forklift access requirements?\n• Building floor load capacity?\n• Fire safety regulations (sprinkler clearance)?\n• Future expansion plans?\n\n*Our Services:*\n• Free site survey & 3D layout\n• Structural calculations\n• Installation by certified teams\n• After-sales maintenance contracts",
      "body_ar": "نصمم أنظمة تخزين تعظم الكفاءة والسلامة.\n\n*الاعتبارات الهندسية:*\n• قدرة التحميل للمستوى؟\n• أبعاد المنتج والوزن؟\n• وصول الرافعة الشوكية؟\n• تحمل أرضية المبنى؟\n• لوائح الحرائق؟\n• خطط التوسع؟\n\n*خدماتنا:*\n• مسح موقع مجاني\n• حسابات هندسية\n• تركيب معتمد\n• عقود صيانة",
      "buttons": [
        { "id": "racks_survey", "title_en": "Request Site Survey", "title_ar": "طلب مسح الموقع" },
        { "id": "racks_quote", "title_en": "Request Quotation", "title_ar": "طلب عرض سعر" }
      ],
      "next_logic": {
        "racks_survey": "schedule_visit_form",
        "racks_quote": "racks_quotation_form"
      }
    },
    "racks_quotation_form": {
      "id": "racks_quotation_form",
      "type": "text",
      "header_en": "Racks & Storage Quotation Form",
      "header_ar": "نموذج عرض سعر الرفوف والتخزين",
      "body_en": "We are excited to design your storage solution.\n\n*Warehouse/Space Information:*\n\n📐 *Facility Details:*\n• Building dimensions (L × W × Clear height)\n• Column grid spacing (if known)\n• Floor type: Concrete / Raised / Other\n• Floor load capacity: ___ kg/m²\n\n📦 *Storage Requirements:*\n• Product type\n• Unit load dimensions (L×W×H)\n• Current inventory quantity\n• Storage method: Pallets / Boxes / Loose items\n• Access frequency: High / Medium / Archive\n\n🔧 *Operational Details:*\n• Equipment: Forklift / Hand truck / Automated\n• Aisle width preference\n• Operating hours & shifts\n• Special: Cold storage / Clean room / Hazmat\n\n⚠️ *Safety & Compliance:*\n• Seismic zone requirements\n• Fire suppression type\n• Safety accessories: Guard rails / Column guards / Mesh\n\n📅 *Timeline:*\n• Target completion date\n• Installation constraints",
      "body_ar": "نحن متحمسون لتصميم حل التخزين.\n\n*معلومات المستودع:*\n\n📐 *تفاصيل المنشأة:*\n• الأبعاد (ط × ع × ارتفاع)\n• تباعد الأعمدة\n• نوع الأرضية: خرسانية / مرتفعة\n• تحمل الأرضية: ___ كجم/م²\n\n📦 *متطلبات التخزين:*\n• نوع المنتج\n• أبعاد الحمولة (ط×ع×ا)\n• كمية المخزون\n• طريقة: Pallets / صناديق / فضفاضة\n• التردد: عالي / متوسط / أرشيف\n\n🔧 *التفاصيل التشغيلية:*\n• المعدات: رافعة / عربة يدوية / أوتوماتيكية\n• عرض الممر\n• ساعات التشغيل والورديات\n• متخصص: بارد / نظيف / خطر\n\n⚠️ *السلامة والامتثال:*\n• متطلبات زلزالية\n• نظام إطفاء الحريق\n• ملحقات الأمان\n\n📅 *الجدول الزمني:*\n• تاريخ الانتهاء\n• قيود التركيب",
      "requires_human_followup": true,
      "next": "quote_submitted"
    },
    "smart_submenu": {
      "id": "smart_submenu",
      "type": "interactive_list",
      "header_en": "🚻 Smart Automatic Toilets (Italian-Designed)",
      "header_ar": "🚻 المراحيض الذكية الأوتوماتيكية",
      "body_en": "We bring *Italian-designed* smart sanitation solutions to the Kingdom.\n\n*Technology Features:*\n• Automatic self-cleaning after every use\n• Remote monitoring via IoT\n• Water-saving (up to 70% reduction)\n• Antibacterial surfaces\n• Designed for high-traffic public areas\n\n*Select your application:*",
      "body_ar": "نقدم حلول الصرف الصحي الذكية *بتصميم إيطالي*.\n\n*الميزات التقنية:*\n• تنظيف ذاتي أوتوماتيكي\n• مراقبة عن بعد عبر IoT\n• توفير المياه (حتى 70%)\n• أسطح مضادة للبكتيريا\n• للمناطق العامة المزدحمة\n\n*اختر التطبيق:*",
      "rows": [
        { "id": "smart_public", "title_en": "SMART® Public Toilets", "title_ar": "مراحيض SMART® العامة" },
        { "id": "smart_plus", "title_en": "PLUS® Premium Models", "title_ar": "نماذج PLUS® الممتازة" },
        { "id": "smart_basic", "title_en": "Basic Automatic Models", "title_ar": "نماذج أوتوماتيكية أساسية" },
        { "id": "smart_safety", "title_en": "Safety Rails & Accessories", "title_ar": "قضبان أمان" },
        { "id": "smart_iot", "title_en": "IoT Monitoring Platform", "title_ar": "منصة مراقبة IoT" }
      ],
      "next": "smart_deep_dive"
    },
    "smart_deep_dive": {
      "id": "smart_deep_dive",
      "type": "interactive_button",
      "body_en": "Transforming public sanitation through innovation.\n\n*Project Assessment:*\n• Location: Highway rest stop / Park / Mall / Airport / Mosque / Beach?\n• Expected daily user volume?\n• Power and water connection availability?\n• Maintenance capability: In-house / Contracted?\n• Integration with smart city infrastructure?\n\n*Our Comprehensive Service:*\n• Site feasibility study\n• Civil works guidance\n• Installation & commissioning\n• Staff training\n• Maintenance contracts with 24/7 support",
      "body_ar": "تحويل الصرف الصحي العام بالابتكار.\n\n*تقييم المشروع:*\n• الموقع: طريق / حديقة / مول / مطار / مسجد / شاطئ؟\n• عدد المستخدمين يومياً؟\n• توفر الكهرباء والمياه؟\n• الصيانة: داخلية / متعاقد؟\n• التكامل مع المدينة الذكية؟\n\n*خدماتنا الشاملة:*\n• دراسة الجدوى\n• إرشادات الأعمال المدنية\n• التركيب والتشغيل\n• تدريب الموظفين\n• عقود صيانة 24/7",
      "buttons": [
        { "id": "smart_quote", "title_en": "Request Project Quote", "title_ar": "طلب عرض سعر" },
        { "id": "smart_contact", "title_en": "Schedule Consultation", "title_ar": "جدولة استشارة" }
      ],
      "next_logic": {
        "smart_quote": "smart_quotation_form",
        "smart_contact": "speak_engineer"
      }
    },
    "smart_quotation_form": {
      "id": "smart_quotation_form",
      "type": "text",
      "header_en": "Smart Toilet Project Form",
      "header_ar": "نموذج مشروع المراحيض الذكية",
      "body_en": "We are honored to prepare a comprehensive smart sanitation proposal.\n\n*Project Information:*\n\n📍 *Location & Site Type:*\n• City/Region:\n• Specific location type (rest stop/park/mall/airport/mosque/beach)\n• Latitude/Longitude (if available)\n\n👥 *User Base:*\n• Expected daily users:\n• Peak hour frequency:\n• User demographics (consumers/workers/travelers)\n• Seasonal variations?\n\n🏗️ *Civil Works:*\n• Building dimensions:\n• Foundation requirements:\n• Water & sewage connections available?\n• Power supply: 220V single/three-phase?\n\n💡 *Technology & Features:*\n• Model preference: SMART® / PLUS® / Basic?\n• IoT monitoring required?\n• Integrated accessibility features needed?\n• Emergency alert systems?\n\n🧹 *Maintenance Plan:*\n• In-house maintenance team available?\n• Spare parts inventory required?\n• Training needs:\n\n📊 *Documentation:*\n• Site drawings/plans available?\n• Building layout (PDF/JPG)\n• Utility maps\n\n⏰ *Project Timeline:*\n• Target implementation date:\n• Phase-based rollout needed?\n• Operational constraints during installation?",
      "body_ar": "نتشرف بإعداد اقتراح شامل للصرف الصحي الذكي.\n\n*معلومات المشروع:*\n\n📍 *الموقع ونوع الموقع:*\n• المدينة/المنطقة:\n• نوع الموقع (استراحة/حديقة/مول/مطار/مسجد/شاطئ)\n• الإحداثيات (إن وُفقت)\n\n👥 *قاعدة المستخدمين:*\n• المستخدمون اليوميون المتوقعون:\n• تردد ساعة الذروة:\n• التركيبة السكانية (مستهلكون/عمال/مسافرون)\n• تغييرات موسمية؟\n\n🏗️ *الأعمال المدنية:*\n• أبعاد المبنى:\n• متطلبات الأساسات:\n• الاتصالات (مياه/صرف) متوفرة؟\n• الكهرباء: أحادي/ثلاثي الطور؟\n\n💡 *التكنولوجيا والميزات:*\n• تفضيل النموذج: SMART® / PLUS® / Basic؟\n• مراقبة IoT مطلوبة؟\n• ميزات إمكانية وصول؟\n• أنظمة تنبيه طوارئ؟\n\n🧹 *خطة الصيانة:*\n• فريق صيانة داخلي متوفر؟\n• مخزون قطع غيار؟\n• احتياجات التدريب:\n\n📊 *المستندات:*\n• رسومات الموقع متوفرة؟\n• مخطط المبنى (PDF/JPG)\n• خرائط المرافق\n\n⏰ *الجدول الزمني:*\n• تاريخ التنفيذ المستهدف:\n• نشر مراحلي؟\n• قيود التشغيل؟",
      "requires_human_followup": true,
      "next": "quote_submitted"
    },
    "quote_submitted": {
      "id": "quote_submitted",
      "type": "text",
      "body_en": "Thank you for providing those details! 🙏\n\nYour quotation request has been received and logged in our system.\n\n*Next Steps:*\n✅ Our engineering team will review your requirements\n✅ A senior representative will contact you within *2-4 working hours*\n✅ We'll prepare a detailed proposal with technical specifications and pricing\n✅ You'll receive comprehensive documentation and drawings\n\n*Your Reference Number:* #AUTO-[timestamp]\n\n*In the meantime:*\n• Feel free to ask any follow-up questions\n• Contact us via WhatsApp or call our office\n• Our team is available Saturday-Thursday, 8:00 AM - 6:00 PM\n\nWe truly appreciate your trust in Hi-Tech Industrial Group. In sha Allah, we look forward to serving you soon! 🇸🇦",
      "body_ar": "شكراً لتزويدكم بهذه التفاصيل! 🙏\n\nتم استلام طلب عرض السعر الخاص بكم وتسجيله في نظامنا.\n\n*الخطوات التالية:*\n✅ سيقوم فريقنا الهندسي بمراجعة متطلباتكم\n✅ سيتواصل معكم ممثل كبير خلال *2-4 ساعات عمل*\n✅ سنعد عرضاً مفصلاً مع المواصفات والتسعير\n✅ ستتلقون وثائق شاملة ورسومات\n\n*رقم المرجع الخاص بكم:* #AUTO-[timestamp]\n\n*في أثناء ذلك:*\n• لا تترددوا في طرح أسئلة متابعة\n• تواصلوا عبر WhatsApp أو اتصلوا بمكتبنا\n• فريقنا متاح السبت-الخميس، 8:00 صباحاً - 6:00 مساءً\n\nنحن ممتنون لثقتكم بمجموعة هي تك الصناعية. بإذن الله، ننتظر شرف خدمتكم قريباً! 🇸🇦",
      "next": "main_menu",
      "analytics_tag": "quote_submitted"
    },
    "speak_engineer": {
      "id": "speak_engineer",
      "type": "text",
      "body_en": "We are connecting you to our sales engineering team.\n\n*Available Expert:*\n👨‍💼 Senior Sales Engineer - Hi-Tech Industrial Group\n\n*Response Time:* Immediate to 15 minutes (during business hours)\n\n*Our Business Hours:*\nSaturday - Thursday: 8:00 AM - 6:00 PM\nFriday: Closed\n⏰ Current time: [server_time]\n\n*Please describe your requirements:*\nShare as much detail as you can about:\n• Your specific need\n• Timeline\n• Budget considerations\n• Any technical constraints\n\nOur engineer will provide expert consultation and help you find the best solution for your project.\n\n*Alternatively, you can call us:*\n📞 +966 (0) [YOUR-PHONE-NUMBER]\n📧 sales@hitech-group.com",
      "body_ar": "نقوم بربطك بفريق مهندسي المبيعات لدينا.\n\n*الخبير المتاح:*\n👨‍💼 مهندس مبيعات كبير - مجموعة هي تك الصناعية\n\n*وقت الرد:* فوري إلى 15 دقيقة (ساعات العمل)\n\n*ساعات عملنا:*\nالسبت - الخميس: 8:00 صباحاً - 6:00 مساءً\nالجمعة: مغلق\n⏰ الوقت الحالي: [server_time]\n\n*يرجى وصف احتياجاتك:*\nشارك أكبر قدر من التفاصيل عن:\n• احتياجك المحدد\n• الجدول الزمني\n• اعتبارات الميزانية\n• أي قيود فنية\n\nسيقدم مهندسنا استشارة خبيرة ويساعدك على إيجاد الحل الأفضل.\n\n*بدلاً من ذلك، يمكنك الاتصال بنا:*\n📞 +966 (0) [YOUR-PHONE-NUMBER]\n📧 sales@hitech-group.com",
      "requires_human_followup": true,
      "next": "main_menu"
    },
    "other_support": {
      "id": "other_support",
      "type": "text",
      "body_en": "Thank you for reaching out to us. We're here to help! 🤝\n\n*How can we assist you?*\n\nThis channel is for:\n✅ Technical support questions\n✅ Complaints or feedback\n✅ Special requests\n✅ Warranty or after-sales issues\n✅ Partnership inquiries\n✅ Any other questions not covered above\n\n*Please describe your request in detail:*\nInclude:\n• What is your concern or question?\n• Which product/service does it relate to?\n• When did the issue occur?\n• What have you already tried?\n• Your preferred solution\n\n*Our Support Team Response:*\n🕐 Typical response time: 1-2 hours (business hours)\n📞 Urgent issues: Call +966 (0) [YOUR-PHONE-NUMBER]\n📧 Email: support@hitech-group.com\n\n*Available:* Saturday-Thursday, 8:00 AM - 6:00 PM\n*Closed:* Friday & Public Holidays",
      "body_ar": "شكراً لتواصلكم معنا. نحن هنا لمساعدتك! 🤝\n\n*كيف يمكننا مساعدتك؟*\n\nهذه القناة للـ:\n✅ أسئلة الدعم الفني\n✅ الشكاوى والملاحظات\n✅ الطلبات الخاصة\n✅ مشاكل الضمان ما بعد البيع\n✅ استفسارات الشراكة\n✅ أي أسئلة أخرى\n\n*يرجى وصف طلبك بالتفصيل:*\nأدرج:\n• ما هو سؤالك أو القلق؟\n• ما المنتج/الخدمة ذات الصلة؟\n• متى حدثت المشكلة؟\n• ماذا جربت بالفعل؟\n• الحل المفضل لديك\n\n*رد فريق الدعم:*\n🕐 الوقت العادي: 1-2 ساعة\n📞 المشاكل العاجلة: +966 (0) [YOUR-PHONE-NUMBER]\n📧 البريد الإلكتروني: support@hitech-group.com\n\n*متاح:* السبت-الخميس، 8:00 صباحاً - 6:00 مساءً\n*مغلق:* الجمعة والعطل الرسمية",
      "requires_human_followup": true,
      "next": "main_menu"
    },
    "schedule_visit_form": {
      "id": "schedule_visit_form",
      "type": "text",
      "body_en": "We would be delighted to schedule a site visit for you!\n\n*Free Site Survey Service Includes:*\n✅ Professional technical assessment\n✅ Measurements and drawings\n✅ 3D layout planning\n✅ Recommendations & optimization\n✅ Preliminary quotation\n\n*Please provide the following:*\n\n📍 *Site Information:*\n• Full address\n• City/District\n• GPS coordinates (if available)\n\n📅 *Preferred Date & Time:*\n• Preferred dates (provide 2-3 options)\n• Preferred time window (morning/afternoon/flexible)\n• Any time constraints?\n\n📝 *Contact Information:*\n• Your name\n• Mobile number\n• Email address (if available)\n• Company name (if applicable)\n\n📋 *Project Details:*\n• Brief description of requirements\n• Estimated budget range\n• Timeline for implementation\n• Any special access requirements?\n\n🗣️ *Communication Preference:*\n• WhatsApp / Call / Email\n\n*Our team will confirm the appointment within 2 hours.*",
      "body_ar": "سيسعدنا جداً جدولة زيارة موقع لك!\n\n*خدمة المسح الموقعي المجانية تشمل:*\n✅ تقييم تقني احترافي\n✅ القياسات والرسومات\n✅ تخطيط أبعاد 3D\n✅ التوصيات والتحسينات\n✅ عرض سعر أولي\n\n*يرجى تزويدنا بـ:*\n\n📍 *معلومات الموقع:*\n• العنوان الكامل\n• المدينة/الحي\n• الإحداثيات (إن وُفقت)\n\n📅 *التاريخ والوقت المفضلان:*\n• التواريخ المفضلة (2-3 خيارات)\n• نافذة الوقت (صباح/مساء/مرن)\n• أي قيود زمنية؟\n\n📝 *معلومات الاتصال:*\n• اسمك\n• رقم الجوال\n• بريد إلكتروني (إن وُفق)\n• اسم الشركة (إن انطبق)\n\n📋 *تفاصيل المشروع:*\n• وصف موجز للمتطلبات\n• نطاق الميزانية المقدرة\n• الجدول الزمني للتنفيذ\n• أي متطلبات وصول خاصة؟\n\n🗣️ *تفضيل الاتصال:*\n• WhatsApp / اتصال / بريد\n\n*سيؤكد فريقنا الموعد خلال ساعتين.*",
      "requires_human_followup": true,
      "next": "quote_submitted"
    },
    "send_document": {
      "id": "send_document",
      "type": "text",
      "body_en": "Thank you for your interest! 📄\n\nWe are preparing to send you the requested documents.\n\n*Documents Available:*\n📄 Company Profile & Certifications\n📊 Technical Specifications (PDF)\n📸 Project Gallery & Case Studies\n🎥 Factory Video Tour (link)\n📋 Product Catalogs & Brochures\n🗂️ Installation Guidelines & Manuals\n\n*Please wait...* Our system is compiling your requested materials.\n\n*Alternatively:*\nYou can download all materials from our website:\n🌐 www.hitech-group.com\n\n*Or contact us directly:*\n📞 +966 (0) [YOUR-PHONE-NUMBER]\n📧 info@hitech-group.com\n\nWe will also have a representative contact you shortly to discuss your specific requirements.",
      "body_ar": "شكراً لاهتمامك! 📄\n\nنحن نستعد لإرسال المستندات المطلوبة.\n\n*المستندات المتاحة:*\n📄 ملف الشركة والشهادات\n📊 المواصفات الفنية (PDF)\n📸 معرض المشاريع ودراسات الحالة\n🎥 جولة المصنع المصورة (رابط)\n📋 الكتالوجات والكتيبات\n🗂️ إرشادات التركيب والمقالات\n\n*يرجى الانتظار...* نحن نجمع مواردك المطلوبة.\n\n*بدلاً من ذلك:*\nيمكنك تحميل جميع المواد من موقعنا:\n🌐 www.hitech-group.com\n\n*أو تواصل معنا مباشرة:*\n📞 +966 (0) [YOUR-PHONE-NUMBER]\n📧 info@hitech-group.com\n\nسيقوم ممثل بالاتصال بك قريباً لمناقشة متطلباتك.",
      "next": "main_menu"
    },
    "send_video": {
      "id": "send_video",
      "type": "text",
      "body_en": "Exciting! 🎥 Here's our factory video tour.\n\n*Hi-Tech Industrial Group - Factory Tour Video*\n📹 Duration: 15 minutes\n🏭 Tour includes:\n  • Raw material handling\n  • Modern manufacturing lines\n  • Quality control laboratory\n  • Skilled workforce\n  • Finished product showcase\n\n*Watch Here:*\n🎬 YouTube: [link-to-video]\n🔗 Direct link: [direct-link]\n\n*Key Highlights:*\n✅ State-of-the-art machinery\n✅ ISO certified processes\n✅ 100% Quality inspection\n✅ Made in Saudi Arabia (Vision 2030 aligned)\n\nWe're proud of our manufacturing excellence and commitment to quality.\n\n*Next Steps:*\nAfter watching, feel free to:\n• Ask technical questions\n• Request a quotation\n• Schedule a physical site visit\n• Speak to our sales team\n\n*Questions?* Contact us anytime! 😊",
      "body_ar": "رائع! 🎥 إليك جولة مصنعنا المصورة.\n\n*جولة مصنع مجموعة هي تك الصناعية*\n📹 المدة: 15 دقيقة\n🏭 الجولة تشمل:\n  • معالجة المواد الخام\n  • خطوط التصنيع الحديثة\n  • مختبر مراقبة الجودة\n  • القوى العاملة الماهرة\n  • عرض المنتجات النهائية\n\n*شاهد هنا:*\n🎬 YouTube: [link-to-video]\n🔗 رابط مباشر: [direct-link]\n\n*الميزات الرئيسية:*\n✅ آلات متطورة\n✅ عمليات معتمدة ISO\n✅ فحص الجودة 100%\n✅ صنع في السعودية (رؤية 2030)\n\nنحن فخورون بتميز التصنيع والتزامنا بالجودة.\n\n*الخطوات التالية:*\nبعد المشاهدة، يمكنك:\n• طرح أسئلة تقنية\n• طلب عرض سعر\n• جدولة زيارة موقعية\n• التحدث مع فريق المبيعات\n\n*أسئلة؟* اتصل بنا في أي وقت! 😊",
      "next": "main_menu"
    },
    "general_inquiry_form": {
      "id": "general_inquiry_form",
      "type": "text",
      "body_en": "Thank you for your general inquiry! We welcome any questions about Hi-Tech Industrial Group.\n\n*What would you like to know?*\n\nPlease tell us:\n\n❓ *Your Question(s):*\n• What is your primary inquiry?\n• Are there any specific products/services you're interested in?\n• What problem are you trying to solve?\n• Do you have any follow-up questions?\n\n👤 *About You:*\n• Your name:\n• Company name (if applicable):\n• Your position/role:\n• Industry/sector you represent:\n\n📞 *Preferred Contact Method:*\n• WhatsApp / Phone / Email\n• Best time to contact you:\n\n📋 *Additional Information:*\n• How did you hear about us?\n• Are you looking to become a partner/distributor?\n• Any other details you'd like to share?\n\n*Our Response:*\n✅ Typical response time: 2-4 hours\n✅ We'll provide comprehensive information\n✅ A team member will follow up if needed\n\nWe look forward to hearing from you!",
      "body_ar": "شكراً على استفسارك العام! نرحب بأي أسئلة عن مجموعة هي تك الصناعية.\n\n*ماذا تود أن تعرف؟*\n\nيرجى أخبرنا:\n\n❓ *سؤالك/أسئلتك:*\n• ما هو استفسارك الأساسي؟\n• هل أنت مهتم بمنتجات/خدمات محددة؟\n• ما المشكلة التي تحاول حلها؟\n• هل لديك أسئلة متابعة؟\n\n👤 *عنك:*\n• اسمك:\n• اسم الشركة (إن انطبق):\n• وظيفتك/دورك:\n• القطاع/الصناعة التي تمثلها:\n\n📞 *طريقة الاتصال المفضلة:*\n• WhatsApp / اتصال / بريد\n• أفضل وقت للاتصال:\n\n📋 *معلومات إضافية:*\n• كيف سمعت عنا؟\n• هل تبحث عن الشراكة/التوزيع؟\n• أي تفاصيل أخرى تود مشاركتها؟\n\n*ردنا:*\n✅ وقت الرد العادي: 2-4 ساعات\n✅ سنقدم معلومات شاملة\n✅ سيتابع معك أحد أعضاء الفريق إذا لزم الأمر\n\nننتظر سماع رأيك بفارغ الصبر!",
      "requires_human_followup": true,
      "next": "quote_submitted"
    }
  },
  "fallback_handlers": {
    "unrecognized_input": {
      "id": "unrecognized_input",
      "type": "text",
      "body_en": "I'm sorry, I didn't quite understand that. 😊\n\nPlease select from the options above, or:\n\n🔄 *What would you like to do?*\n• Go back to Main Menu\n• Speak to a Sales Engineer\n• Request General Support\n\nIf you're having trouble, please type 'help' or contact us directly at:\n📞 +966 (0) [YOUR-PHONE-NUMBER]\n📧 support@hitech-group.com",
      "body_ar": "أعتذر، لم أفهم تماماً. 😊\n\nيرجى اختيار من الخيارات أعلاه، أو:\n\n🔄 *ماذا تود أن تفعل؟*\n• العودة إلى القائمة الرئيسية\n• التحدث مع مهندس مبيعات\n• طلب دعم عام\n\nإذا كنت تواجه مشاكل، يرجى كتابة 'help' أو اتصل بنا مباشرة:\n📞 +966 (0) [YOUR-PHONE-NUMBER]\n📧 support@hitech-group.com"
    },
    "session_timeout": {
      "id": "session_timeout",
      "type": "text",
      "body_en": "Your session has expired due to inactivity.\n\n👋 Welcome back! Would you like to:\n\n🔄 Start over from the Main Menu?\nor\n☎️ Continue with your previous inquiry?\n\nPlease let us know how we can assist you.",
      "body_ar": "انتهت جلستك بسبب عدم النشاط.\n\n👋 أهلاً بك مرة أخرى! هل تود:\n\n🔄 البدء من جديد من القائمة الرئيسية؟\nأو\n☎️ المتابعة مع استفسارك السابق؟\n\nيرجى إخبرنا كيف يمكننا مساعدتك."
    },
    "human_handoff_request": {
      "id": "human_handoff_request",
      "type": "text",
      "body_en": "You've requested to speak with our team. 🤝\n\n*Connecting you now...*\n\nWhile you wait, please provide:\n\n1️⃣ *Your Name:*\n2️⃣ *Your Contact Number:*\n3️⃣ *Brief Description of Your Inquiry:*\n4️⃣ *Preferred Contact Method:* (WhatsApp / Call / Email)\n\n*Expected Response Time:* 5-15 minutes (during business hours)\n\n*Our Hours:*\nSaturday-Thursday: 8:00 AM - 6:00 PM\nFriday: Closed\n\nThank you for your patience! 😊",
      "body_ar": "لقد طلبت التحدث مع فريقنا. 🤝\n\n*نقوم بربطك الآن...*\n\nبينما تنتظر، يرجى توفير:\n\n1️⃣ *اسمك:*\n2️⃣ *رقم هاتفك:*\n3️⃣ *وصف موجز لاستفسارك:*\n4️⃣ *طريقة الاتصال المفضلة:* (WhatsApp / اتصال / بريد)\n\n*وقت الرد المتوقع:* 5-15 دقيقة (ساعات العمل)\n\n*ساعات عملنا:*\nالسبت-الخميس: 8:00 صباحاً - 6:00 مساءً\nالجمعة: مغلق\n\nشكراً لصبرك! 😊"
    }
  }
};

const state = {
  currentStep: 'welcome',
  language: 'en'
};

const chatPanel = document.getElementById('chat-panel');
const optionsContainer = document.getElementById('options-container');
const stepTitleEl = document.getElementById('step-title');
const stepIdEl = document.getElementById('step-id');
const restartButton = document.getElementById('restart-button');

function sanitize(text) {
  return text.replace(/\n/g, '<br/>');
}

function formatStepText(step) {
  const header = step.header_en ? `<strong>${step.header_en}</strong><br/><br/>` : '';
  const body = step.body_en || step.message_en || '';
  return sanitize(`${header}${body}`);
}

function renderMessage({text, sender}) {
  const row = document.createElement('div');
  row.className = `message-row ${sender}`;
  row.innerHTML = `
    <div>
      <div class="${sender}-label">${sender === 'bot' ? 'Hi-Tech Bot' : 'You'}</div>
      <div class="message-bubble ${sender}">${text}</div>
    </div>
  `;
  chatPanel.appendChild(row);
  chatPanel.scrollTop = chatPanel.scrollHeight;
}

function resolveNextStep(step, selectionId) {
  if (step.next_logic && step.next_logic[selectionId]) {
    return step.next_logic[selectionId];
  }
  if (step.next) {
    return step.next;
  }
  return null;
}

function flattenMenuOptions(step) {
  const items = [];
  if (step.sections) {
    step.sections.forEach(section => {
      section.rows.forEach(row => {
        items.push({ id: row.id, label: row.title_en || row.title || row.id });
      });
    });
  }
  if (step.rows) {
    step.rows.forEach(row => {
      items.push({ id: row.id, label: row.title_en || row.title || row.id });
    });
  }
  return items;
}

function renderOptions(step) {
  optionsContainer.innerHTML = '';

  if (step.type === 'interactive_button') {
    step.buttons.forEach(button => {
      const action = document.createElement('button');
      action.className = 'action-button';
      action.innerHTML = `<strong>${button.title_en}</strong>`;
      action.addEventListener('click', () => handleUserChoice(button.id, button.title_en));
      optionsContainer.appendChild(action);
    });
    return;
  }

  if (step.type === 'interactive_list') {
    const rows = flattenMenuOptions(step);
    rows.forEach(row => {
      const action = document.createElement('button');
      action.className = 'action-button';
      action.innerHTML = `<strong>${row.label}</strong>`;
      action.addEventListener('click', () => handleUserChoice(row.id, row.label));
      optionsContainer.appendChild(action);
    });
    return;
  }

  if (step.type === 'text') {
    if (step.requires_human_followup || step.id.includes('_form')) {
      const wrapper = document.createElement('div');
      wrapper.className = 'input-row';

      const textarea = document.createElement('textarea');
      textarea.placeholder = 'Type your response here to continue...';
      textarea.id = 'user-input';

      const sendButton = document.createElement('button');
      sendButton.textContent = 'Send';
      sendButton.addEventListener('click', () => {
        const value = textarea.value.trim();
        if (!value) return;
        handleUserInput(value);
      });

      wrapper.appendChild(textarea);
      wrapper.appendChild(sendButton);
      optionsContainer.appendChild(wrapper);
      return;
    }

    const nextStepId = resolveNextStep(step);
    if (nextStepId) {
      const action = document.createElement('button');
      action.className = 'action-button';
      action.textContent = 'Continue';
      action.addEventListener('click', () => gotoStep(nextStepId));
      optionsContainer.appendChild(action);
      return;
    }

    const mainAction = document.createElement('button');
    mainAction.className = 'action-button';
    mainAction.textContent = 'Back to Main Menu';
    mainAction.addEventListener('click', () => gotoStep('main_menu'));
    optionsContainer.appendChild(mainAction);
  }
}

function nextStepForSelection(step, selectionId) {
  if (step.next_logic && step.next_logic[selectionId]) {
    return step.next_logic[selectionId];
  }
  if (step.next) {
    return step.next;
  }
  return null;
}

function handleUserChoice(id, label) {
  renderMessage({sender: 'user', text: label});
  const step = chatflow.steps[state.currentStep];
  const nextId = nextStepForSelection(step, id);
  if (!nextId) {
    gotoStep('unrecognized_input');
    return;
  }
  setTimeout(() => gotoStep(nextId), 300);
}

function handleUserInput(value) {
  renderMessage({sender: 'user', text: value});
  const step = chatflow.steps[state.currentStep];
  const nextId = resolveNextStep(step);
  if (!nextId) {
    gotoStep('unrecognized_input');
    return;
  }
  setTimeout(() => gotoStep(nextId), 400);
}

function getDisplayText(step) {
  const content = step.header_en ? `${step.header_en}\n\n${step.body_en || ''}` : (step.body_en || step.message_en || '');
  return content || '...';
}

function gotoStep(stepId) {
  state.currentStep = stepId;
  const step = chatflow.steps[stepId] || chatflow.fallback_handlers[stepId];
  if (!step) {
    renderMessage({sender: 'bot', text: 'Sorry, this step is missing in the preview.'});
    return;
  }

  stepTitleEl.innerHTML = step.header_en ? step.header_en : (step.body_en ? step.body_en.split('\n')[0] : stepId);
  stepIdEl.textContent = `Step ID: ${stepId}`;

  const botText = getDisplayText(step);
  renderMessage({sender: 'bot', text: botText});
  renderOptions(step);
}

function attachQuickButtons() {
  document.querySelectorAll('.quick-button').forEach(button => {
    button.addEventListener('click', () => gotoStep(button.dataset.step));
  });
}

function resetConversation() {
  chatPanel.innerHTML = '';
  optionsContainer.innerHTML = '';
  gotoStep('welcome');
}

window.addEventListener('DOMContentLoaded', () => {
  attachQuickButtons();
  restartButton.addEventListener('click', resetConversation);
  resetConversation();
});
