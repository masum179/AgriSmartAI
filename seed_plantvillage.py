import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agrismart.settings')
django.setup()

from detection.models import Disease, Recommendation

DISEASE_DATA = [
    # Tomato
    {
        "name_en": "Tomato Bacterial Spot", "name_bn": "টমেটোর ব্যাকটেরিয়াল স্পট", "crop_type": "Tomato", "severity": "medium",
        "desc": "পাতায় ছোট, পানি ভেজা দাগ দেখা দেয় যা পরে গাঢ় বাদামী বা কালো রঙের হয়ে যায়।",
        "treat": "কপার যুক্ত ছত্রাকনাশক স্প্রে করুন।", "pest": "কপার অক্সিক্লোরাইড (Copper Oxychloride)", "prev": "রোগমুক্ত বীজ ব্যবহার করুন এবং ফসলের অবশিষ্টাংশ ধ্বংস করুন।"
    },
    {
        "name_en": "Tomato Early Blight", "name_bn": "টমেটোর আর্লি ব্লাইট", "crop_type": "Tomato", "severity": "high",
        "desc": "পাতায় কালচে বাদামী রঙের বৃত্তাকার দাগ দেখা যায়। ধীরে ধীরে পাতা শুকিয়ে যায়।",
        "treat": "ম্যানকোজেব বা ক্লোরোথালোনিল জাতীয় ছত্রাকনাশক প্রয়োগ করুন।", "pest": "ম্যানকোজেব (Mancozeb)", "prev": "মাটিতে পানি জমতে দেবেন না এবং পর্যাপ্ত আলো বাতাসের ব্যবস্থা রাখুন।"
    },
    {
        "name_en": "Tomato Late Blight", "name_bn": "টমেটোর লেট ব্লাইট", "crop_type": "Tomato", "severity": "high",
        "desc": "পাতায় বড়, অনিয়মিত জলসিক্ত দাগ দেখা দেয়। আর্দ্র আবহাওয়ায় দাগগুলো দ্রুত বাড়ে।",
        "treat": "মেটালাক্সিল ও ম্যানকোজেব এর মিশ্রণ স্প্রে করুন।", "pest": "রিডোমিল গোল্ড (Ridomil Gold)", "prev": "আর্দ্র আবহাওয়ায় আগাম ছত্রাকনাশক স্প্রে করুন।"
    },
    {
        "name_en": "Tomato Leaf Mold", "name_bn": "টমেটোর লিফ মোল্ড", "crop_type": "Tomato", "severity": "medium",
        "desc": "পাতার উপরের অংশে ফ্যাকাশে সবুজ বা হলুদ দাগ দেখা যায় এবং নিচের দিকে জলপাই রঙের ছাঁচ জন্মায়।",
        "treat": "বায়ু চলাচল বৃদ্ধি করুন এবং ছত্রাকনাশক স্প্রে করুন।", "pest": "কার্বেন্ডাজিম (Carbendazim)", "prev": "গ্রিনহাউসে আর্দ্রতা নিয়ন্ত্রণ করুন।"
    },
    {
        "name_en": "Tomato Septoria Leaf Spot", "name_bn": "টমেটোর সেপ্টোরিয়া লিফ স্পট", "crop_type": "Tomato", "severity": "medium",
        "desc": "পুরানো পাতায় ছোট, গোলাকার এবং কেন্দ্র ধূসর রঙের দাগ দেখা যায়।",
        "treat": "ক্লোরোথালোনিল জাতীয় ছত্রাকনাশক প্রয়োগ করুন।", "pest": "ক্লোরোথালোনিল (Chlorothalonil)", "prev": "নিচের দিকের আক্রান্ত পাতা ছিঁড়ে ফেলুন।"
    },
    {
        "name_en": "Tomato Spider Mites", "name_bn": "টমেটোর মাকড়সা পোকা (স্পাইডার মাইটস)", "crop_type": "Tomato", "severity": "high",
        "desc": "পাতায় ছোট হলুদ বা সাদা বিন্দু দেখা যায়। তীব্র আক্রমণে পাতায় জালের মতো দেখা যায়।",
        "treat": "মাকড়নাশক স্প্রে করুন।", "pest": "অ্যাবামেকটিন (Abamectin)", "prev": "গাছ পরিষ্কার রাখুন এবং খরা পরিহার করুন।"
    },
    {
        "name_en": "Tomato Target Spot", "name_bn": "টমেটোর টার্গেট স্পট", "crop_type": "Tomato", "severity": "medium",
        "desc": "পাতায় হালকা বাদামী দাগ যা রিং আকৃতির হয়।",
        "treat": "ছত্রাকনাশক স্প্রে করুন।", "pest": "অ্যাজোক্সিস্ট্রবিন (Azoxystrobin)", "prev": "সুষম সার প্রয়োগ করুন।"
    },
    {
        "name_en": "Tomato Yellow Leaf Curl Virus", "name_bn": "টমেটোর ইয়েলো লিফ কার্ল ভাইরাস", "crop_type": "Tomato", "severity": "high",
        "desc": "পাতা হলুদ হয়ে যায়, কুঁচকে যায় এবং গাছের বৃদ্ধি থেমে যায়।",
        "treat": "সাদা মাছি দমন করুন যা এই ভাইরাস ছড়ায়। আক্রান্ত গাছ তুলে ধ্বংস করুন।", "pest": "ইমিডাক্লোপ্রিড (Imidacloprid)", "prev": "সাদা মাছি রোধক জাত ব্যবহার করুন।"
    },
    {
        "name_en": "Tomato Mosaic Virus", "name_bn": "টমেটো মোজাইক ভাইরাস", "crop_type": "Tomato", "severity": "medium",
        "desc": "পাতায় হালকা ও গাঢ় সবুজ রঙের ছোপ ছোপ দাগ দেখা দেয়। পাতা বিকৃত হয়ে যায়।",
        "treat": "আক্রান্ত গাছ দ্রুত তুলে ফেলে ধ্বংস করুন। ভাইরাসের কোনো সরাসরি চিকিৎসা নেই।", "pest": "প্রযোজ্য নয়", "prev": "ভাইরাসমুক্ত বীজ ব্যবহার করুন এবং কাজ করার সময় হাত পরিষ্কার রাখুন।"
    },
    {
        "name_en": "Tomato Healthy", "name_bn": "সুস্থ টমেটো গাছ", "crop_type": "Tomato", "severity": "low",
        "desc": "গাছ সম্পূর্ণ সুস্থ আছে। কোনো রোগের লক্ষণ নেই।",
        "treat": "বর্তমান পরিচর্যা চালিয়ে যান।", "pest": "প্রয়োজন নেই", "prev": "নিয়মিত পর্যবেক্ষণ করুন।"
    },

    # Potato
    {
        "name_en": "Potato Early Blight", "name_bn": "আলুর আর্লি ব্লাইট", "crop_type": "Potato", "severity": "medium",
        "desc": "আলুর পাতায় ছোট বাদামী রঙের দাগ পড়ে, যা পরে বড় হয়ে রিং আকৃতি ধারণ করে।",
        "treat": "সঠিক সময়ে ছত্রাকনাশক স্প্রে করুন।", "pest": "ম্যানকোজেব (Mancozeb)", "prev": "ফসল আবর্তন (Crop rotation) অনুসরণ করুন।"
    },
    {
        "name_en": "Potato Late Blight", "name_bn": "আলুর লেট ব্লাইট (মড়ক রোগ)", "crop_type": "Potato", "severity": "high",
        "desc": "পাতার কিনারায় জলসিক্ত দাগ পড়ে যা পরে কালো হয়ে যায় এবং পাতা পচে যায়।",
        "treat": "দ্রুত ছত্রাকনাশক স্প্রে করুন।", "pest": "মেটালাক্সিল + ম্যানকোজেব", "prev": "রোগ প্রতিরোধী জাত ব্যবহার করুন।"
    },
    {
        "name_en": "Potato Scab", "name_bn": "আলুর স্ক্যাব", "crop_type": "Potato", "severity": "medium",
        "desc": "আলুর গায়ে খসখসে, কর্কের মতো দাগ দেখা যায়।",
        "treat": "মাটির পিএইচ (pH) ৫.০ থেকে ৫.২ এর মধ্যে রাখুন।", "pest": "প্রযোজ্য নয়", "prev": "সুস্থ বীজ আলু রোপণ করুন।"
    },
    {
        "name_en": "Potato Healthy", "name_bn": "সুস্থ আলু গাছ", "crop_type": "Potato", "severity": "low",
        "desc": "গাছ সম্পূর্ণ সুস্থ আছে।",
        "treat": "বর্তমান পরিচর্যা চালিয়ে যান।", "pest": "প্রয়োজন নেই", "prev": "নিয়মিত সেচ ও সার দিন।"
    },

    # Corn
    {
        "name_en": "Corn Northern Leaf Blight", "name_bn": "ভুট্টার নর্দার্ন লিফ ব্লাইট", "crop_type": "Corn", "severity": "medium",
        "desc": "ভুট্টার পাতায় লম্বা, ধূসর বা বাদামী দাগ দেখা যায়।",
        "treat": "ছত্রাকনাশক প্রয়োগ করুন।", "pest": "প্রোপিকোনাজল (Propiconazole)", "prev": "প্রতিরোধী জাত ব্যবহার করুন।"
    },
    {
        "name_en": "Corn Common Rust", "name_bn": "ভুট্টার সাধারণ মরিচা রোগ", "crop_type": "Corn", "severity": "medium",
        "desc": "পাতার উভয় দিকে লালচে-বাদামী রঙের মরিচার মতো দাগ দেখা যায়।",
        "treat": "উপযুক্ত ছত্রাকনাশক স্প্রে করুন।", "pest": "অ্যাজোক্সিস্ট্রবিন (Azoxystrobin)", "prev": "আর্দ্র আবহাওয়ায় আগাম সতর্কতা অবলম্বন করুন।"
    },
    {
        "name_en": "Corn Gray Leaf Spot", "name_bn": "ভুট্টার গ্রে লিফ স্পট", "crop_type": "Corn", "severity": "high",
        "desc": "পাতায় আয়তাকার, ধূসর রঙের দাগ দেখা যায়।",
        "treat": "ছত্রাকনাশক স্প্রে করুন এবং আক্রান্ত পাতা সরিয়ে ফেলুন।", "pest": "পাইরাক্লোস্ট্রবিন (Pyraclostrobin)", "prev": "ফসল আবর্তন করুন।"
    },
    {
        "name_en": "Corn Healthy", "name_bn": "সুস্থ ভুট্টা গাছ", "crop_type": "Corn", "severity": "low",
        "desc": "গাছ সম্পূর্ণ সুস্থ আছে।",
        "treat": "বর্তমান পরিচর্যা চালিয়ে যান।", "pest": "প্রয়োজন নেই", "prev": "পর্যাপ্ত সার ও সেচ নিশ্চিত করুন।"
    },

    # Apple
    {
        "name_en": "Apple Scab", "name_bn": "আপেলের স্ক্যাব রোগ", "crop_type": "Apple", "severity": "high",
        "desc": "আপেল এবং পাতায় জলপাই-সবুজ থেকে কালো রঙের দাগ দেখা যায়।",
        "treat": "বসন্তকালে প্রতিরোধক ছত্রাকনাশক স্প্রে করুন।", "pest": "ক্যাপটান (Captan)", "prev": "ঝরে পড়া পাতা পরিষ্কার করুন।"
    },
    {
        "name_en": "Apple Fire Blight", "name_bn": "আপেলের ফায়ার ব্লাইট", "crop_type": "Apple", "severity": "high",
        "desc": "ফুল এবং ডালপালা পুড়ে যাওয়ার মতো কালো হয়ে শুকিয়ে যায়।",
        "treat": "আক্রান্ত ডাল কেটে পুড়িয়ে ফেলুন। ব্যাকটেরিয়ানাশক প্রয়োগ করুন।", "pest": "স্ট্রেপ্টোমাইসিন (Streptomycin)", "prev": "সুস্থ ও নিরোগ চারা রোপণ করুন।"
    },
    {
        "name_en": "Apple Powdery Mildew", "name_bn": "আপেলের পাউডারি মিলডিউ", "crop_type": "Apple", "severity": "medium",
        "desc": "পাতা এবং ডালে সাদা পাউডারের মতো আবরণ তৈরি হয়।",
        "treat": "সালফার বা অন্যান্য উপযুক্ত ছত্রাকনাশক ব্যবহার করুন।", "pest": "সালফার (Sulfur 80% WP)", "prev": "ডালপালা ছেঁটে পর্যাপ্ত বাতাস চলাচলের ব্যবস্থা করুন।"
    },
    {
        "name_en": "Apple Healthy", "name_bn": "সুস্থ আপেল গাছ", "crop_type": "Apple", "severity": "low",
        "desc": "গাছ সম্পূর্ণ সুস্থ আছে।",
        "treat": "নিয়মিত পরিচর্যা করুন।", "pest": "প্রয়োজন নেই", "prev": "সঠিক সময়ে প্রুনিং (ডাল ছাঁটাই) করুন।"
    },

    # Grape
    {
        "name_en": "Grape Downy Mildew", "name_bn": "আঙ্গুরের ডাউনি মিলডিউ", "crop_type": "Grape", "severity": "high",
        "desc": "পাতার উপরের অংশে হলুদ দাগ এবং নিচের অংশে সাদা তুলার মতো ছোপ দেখা যায়।",
        "treat": "কপার বা মেটালাক্সিল যুক্ত ছত্রাকনাশক স্প্রে করুন।", "pest": "রিডোমিল (Ridomil)", "prev": "আর্দ্রতা কমাতে ডালপালা ছেঁটে দিন।"
    },
    {
        "name_en": "Grape Powdery Mildew", "name_bn": "আঙ্গুরের পাউডারি মিলডিউ", "crop_type": "Grape", "severity": "medium",
        "desc": "আঙ্গুর এবং পাতায় ছাই রঙের পাউডারের মতো আস্তরণ পড়ে।",
        "treat": "সালফার যুক্ত ছত্রাকনাশক স্প্রে করুন।", "pest": "হেক্সাকোনাজল (Hexaconazole)", "prev": "গাছে পর্যাপ্ত রোদ নিশ্চিত করুন।"
    },
    {
        "name_en": "Grape Black Rot", "name_bn": "আঙ্গুরের ব্ল্যাক রট", "crop_type": "Grape", "severity": "high",
        "desc": "আঙ্গুরগুলো পচে কালো রঙের শক্ত দানায় পরিণত হয়।",
        "treat": "আক্রান্ত ফল ও পাতা সরিয়ে ফেলুন এবং ছত্রাকনাশক দিন।", "pest": "ম্যানকোজেব (Mancozeb)", "prev": "শীতকালে বাগান পরিষ্কার রাখুন।"
    },
    {
        "name_en": "Grape Healthy", "name_bn": "সুস্থ আঙ্গুর গাছ", "crop_type": "Grape", "severity": "low",
        "desc": "গাছ সম্পূর্ণ সুস্থ আছে।",
        "treat": "বর্তমান পরিচর্যা চালিয়ে যান।", "pest": "প্রয়োজন নেই", "prev": "পর্যাপ্ত সূর্যালোক এবং সেচ দিন।"
    },

    # Wheat & Rice (Cereals)
    {
        "name_en": "Wheat Rust", "name_bn": "গমের মরিচা রোগ", "crop_type": "Wheat", "severity": "high",
        "desc": "গমের পাতা ও কান্ডে লালচে বা হলুদ রঙের মরিচার মতো দাগ দেখা যায়।",
        "treat": "প্রোপিকোনাজল বা টেবিুকোনাজল স্প্রে করুন।", "pest": "টিল্ট ২৫০ ইসি (Tilt 250 EC)", "prev": "প্রতিরোধী গমের জাত ব্যবহার করুন।"
    },
    {
        "name_en": "Rice Blast", "name_bn": "ধানের ব্লাস্ট রোগ", "crop_type": "Rice", "severity": "high",
        "desc": "ধানের পাতায় চোখের মতো আকৃতির দাগ হয় যার মাঝখানটা ছাই রঙের এবং কিনারা বাদামী।",
        "treat": "ট্রাইসাইক্লাজোল জাতীয় ছত্রাকনাশক ব্যবহার করুন।", "pest": "ট্রুপার ৭৫ ডব্লিউপি (Trooper 75 WP)", "prev": "অতিরিক্ত ইউরিয়া সার ব্যবহার পরিহার করুন।"
    },
    {
        "name_en": "Rice Brown Spot", "name_bn": "ধানের বাদামী দাগ রোগ", "crop_type": "Rice", "severity": "medium",
        "desc": "পাতায় ছোট, ডিম্বাকার গাঢ় বাদামী রঙের দাগ দেখা দেয়।",
        "treat": "সুষম মাত্রায় সার ব্যবহার করুন এবং ছত্রাকনাশক দিন।", "pest": "প্রোপিকোনাজল (Propiconazole)", "prev": "বীজ শোধন করে বপন করুন।"
    },
    {
        "name_en": "Rice Healthy", "name_bn": "সুস্থ ধান গাছ", "crop_type": "Rice", "severity": "low",
        "desc": "ধান গাছ সুস্থ আছে।",
        "treat": "পর্যাপ্ত পানি ও সার দিন।", "pest": "প্রয়োজন নেই", "prev": "নিয়মিত মাঠ পরিদর্শন করুন।"
    },
    {
        "name_en": "Wheat Healthy", "name_bn": "সুস্থ গম গাছ", "crop_type": "Wheat", "severity": "low",
        "desc": "গম গাছ সুস্থ আছে।",
        "treat": "পর্যাপ্ত পানি ও সার দিন।", "pest": "প্রয়োজন নেই", "prev": "নিয়মিত মাঠ পরিদর্শন করুন।"
    },

    # Pepper
    {
        "name_en": "Pepper Bacterial Spot", "name_bn": "মরিচের ব্যাকটেরিয়াল স্পট", "crop_type": "Pepper", "severity": "medium",
        "desc": "পাতায় ছোট, পানি ভেজা দাগ যা পরে কালচে খয়েরি হয়ে যায়।",
        "treat": "কপার যুক্ত ছত্রাকনাশক স্প্রে করুন।", "pest": "কপার অক্সিক্লোরাইড (Copper Oxychloride)", "prev": "বৃষ্টির পানি জমতে দেবেন না।"
    },
    {
        "name_en": "Pepper Healthy", "name_bn": "সুস্থ মরিচ গাছ", "crop_type": "Pepper", "severity": "low",
        "desc": "মরিচ গাছ সম্পূর্ণ সুস্থ।",
        "treat": "পরিচর্যা চালিয়ে যান।", "pest": "প্রয়োজন নেই", "prev": "নিয়মিত আগাছা পরিষ্কার করুন।"
    },

    # Strawberry
    {
        "name_en": "Strawberry Leaf Scorch", "name_bn": "স্ট্রবেরির লিফ স্কর্চ", "crop_type": "Strawberry", "severity": "medium",
        "desc": "পাতায় বেগুনি থেকে লালচে দাগ দেখা যায়।",
        "treat": "আক্রান্ত পাতা কেটে ফেলুন এবং ছত্রাকনাশক দিন।", "pest": "ক্যাপটান (Captan)", "prev": "গাছের মাঝে ফাঁকা জায়গা রাখুন।"
    },
    {
        "name_en": "Strawberry Healthy", "name_bn": "সুস্থ স্ট্রবেরি গাছ", "crop_type": "Strawberry", "severity": "low",
        "desc": "গাছ সম্পূর্ণ সুস্থ আছে।",
        "treat": "নিয়মিত যত্ন নিন।", "pest": "প্রয়োজন নেই", "prev": "মাটিতে মালচিং ব্যবহার করুন।"
    },
    
    # Cassava
    {
        "name_en": "Cassava Mosaic Disease", "name_bn": "কাসাভা মোজাইক রোগ", "crop_type": "Cassava", "severity": "high",
        "desc": "পাতায় হলুদ এবং সবুজ ছোপ দেখা যায় এবং পাতা কুঁচকে যায়।",
        "treat": "আক্রান্ত গাছ সমূলে তুলে পুড়িয়ে ফেলুন।", "pest": "সাদা মাছি দমনে কীটনাশক দিন", "prev": "ভাইরাসমুক্ত কাটিং ব্যবহার করুন।"
    },
    {
        "name_en": "Cassava Healthy", "name_bn": "সুস্থ কাসাভা গাছ", "crop_type": "Cassava", "severity": "low",
        "desc": "গাছ সুস্থ আছে।",
        "treat": "বর্তমান পরিচর্যা চালিয়ে যান।", "pest": "প্রয়োজন নেই", "prev": "নিয়মিত জমি আগাছামুক্ত রাখুন।"
    }
]

print(f"Seeding {len(DISEASE_DATA)} PlantVillage diseases...")

count = 0
for data in DISEASE_DATA:
    disease, created = Disease.objects.get_or_create(
        name_en=data['name_en'],
        defaults={
            'name_bn': data['name_bn'],
            'description_bn': data['desc'],
            'crop_type': data['crop_type'],
            'severity': data['severity'],
            'is_active': True
        }
    )
    
    if not created:
        # Update existing records
        disease.name_bn = data['name_bn']
        disease.description_bn = data['desc']
        disease.crop_type = data['crop_type']
        disease.severity = data['severity']
        disease.is_active = True
        disease.save()
        
    # Add/Update Recommendation
    rec, rec_created = Recommendation.objects.get_or_create(
        disease=disease,
        treatment_bn=data['treat'],
        defaults={
            'pesticide_bn': data['pest'],
            'prevention_bn': data['prev']
        }
    )
    
    if not rec_created:
        rec.pesticide_bn = data['pest']
        rec.prevention_bn = data['prev']
        rec.save()

    count += 1

print(f"Successfully processed {count} diseases and their recommendations!")
