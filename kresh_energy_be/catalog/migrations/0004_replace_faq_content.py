from django.db import migrations

NEW_FAQS = [
    {
        "id": 1,
        "category": "general",
        "order": 1,
        "question_de": "Lohnt sich Photovoltaik für jedes Haus?",
        "question_en": "Is solar worth it for every home?",
        "question_ar": "هل تناسب الطاقة الشمسية كل منزل؟",
        "answer_de": (
            "Nicht immer gleich. Entscheidend sind Dachfläche, Ausrichtung, "
            "Verbrauch und Stromkosten. Deshalb prüfen wir jedes Projekt individuell."
        ),
        "answer_en": (
            "Not always in the same way. What matters is roof area, orientation, "
            "consumption and electricity costs. That's why we assess every project individually."
        ),
        "answer_ar": (
            "ليس دائماً بنفس الطريقة. العوامل المهمة هي مساحة السقف، الاتجاه، "
            "الاستهلاك، وتكاليف الكهرباء. لذلك نفحص كل مشروع بشكل فردي."
        ),
    },
    {
        "id": 2,
        "category": "battery",
        "order": 2,
        "question_de": "Brauche ich unbedingt einen Batteriespeicher?",
        "question_en": "Do I necessarily need a battery storage system?",
        "question_ar": "هل أحتاج بالضرورة إلى بطارية تخزين؟",
        "answer_de": (
            "Nicht unbedingt. Ein Speicher kann sinnvoll sein, wenn Sie mehr eigenen "
            "Solarstrom selbst nutzen möchten. Die passende Größe hängt vom Verbrauch ab."
        ),
        "answer_en": (
            "Not necessarily. A storage system can make sense if you want to use more "
            "of your own solar power yourself. The right size depends on your consumption."
        ),
        "answer_ar": (
            "ليس بالضرورة. البطارية قد تكون مفيدة إذا كنت تريد استخدام جزء أكبر من "
            "الكهرباء الشمسية بنفسك. الحجم المناسب يعتمد على استهلاكك."
        ),
    },
    {
        "id": 3,
        "category": "technical",
        "order": 3,
        "question_de": "Kann ich mein E-Auto mit Solarstrom laden?",
        "question_en": "Can I charge my EV with solar power?",
        "question_ar": "هل يمكنني شحن سيارتي الكهربائية بالطاقة الشمسية؟",
        "answer_de": (
            "Ja. Eine Wallbox kann mit der Photovoltaikanlage und optional mit einem "
            "Speicher kombiniert werden."
        ),
        "answer_en": (
            "Yes. A wallbox can be combined with your solar system and, optionally, "
            "with a battery storage system."
        ),
        "answer_ar": (
            "نعم. يمكن ربط شاحن السيارة الكهربائية مع نظام الطاقة الشمسية، ومع بطارية "
            "تخزين إذا كان ذلك مناسباً."
        ),
    },
    {
        "id": 4,
        "category": "general",
        "order": 4,
        "question_de": "Wie bekomme ich ein Angebot?",
        "question_en": "How do I get a quote?",
        "question_ar": "كيف أحصل على عرض؟",
        "answer_de": (
            "Sie senden uns Ihre Anfrage. Danach prüfen wir Ihre Angaben und melden "
            "uns mit einer ersten Einschätzung."
        ),
        "answer_en": (
            "You send us your request. We then review your details and get back to "
            "you with an initial assessment."
        ),
        "answer_ar": (
            "ترسل لنا طلبك. بعد ذلك نراجع المعلومات ونتواصل معك بتقييم أولي."
        ),
    },
    {
        "id": 5,
        "category": "general",
        "order": 5,
        "question_de": "Ist die Beratung kostenlos?",
        "question_en": "Is the consultation free?",
        "question_ar": "هل الاستشارة مجانية؟",
        "answer_de": "Die erste Einschätzung ist kostenlos und unverbindlich.",
        "answer_en": "The initial assessment is free and non-binding.",
        "answer_ar": "التقييم الأولي مجاني وبدون التزام.",
    },
]


def replace_faqs(apps, schema_editor):
    FAQ = apps.get_model("catalog", "FAQ")
    FAQ.objects.all().delete()
    for data in NEW_FAQS:
        FAQ.objects.create(**data)


def restore_previous_faqs(apps, schema_editor):
    FAQ = apps.get_model("catalog", "FAQ")
    FAQ.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0003_calculatorconfig"),
    ]

    operations = [
        migrations.RunPython(replace_faqs, restore_previous_faqs),
    ]
