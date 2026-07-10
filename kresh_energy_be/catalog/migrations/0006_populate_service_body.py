from django.db import migrations

# pk -> slug, per fixtures/seed.json:
# 1=solaranlagen-installation 2=batteriespeicher 3=wallbox-ladeloesungen
# 4=anlagenpruefung 5=wartung 6=gewerbeloesungen
BODY_CONTENT = {
    1: {
        "body_de": (
            "Eine Photovoltaik-Anlage ist die Basis für Ihre eigene, saubere "
            "Energieversorgung. Wir übernehmen die komplette Planung – von der "
            "ersten Dachanalyse über die Auslegung der Module und Wechselrichter "
            "bis zur Anmeldung beim Netzbetreiber.\n\n"
            "Bei der Montage setzen wir ausschließlich auf zertifizierte "
            "Fachbetriebe und hochwertige Komponenten. So stellen wir sicher, "
            "dass Ihre Anlage nicht nur zuverlässig, sondern auch über "
            "Jahrzehnte hinweg sicher läuft.\n\n"
            "Ob Satteldach, Flachdach oder Fassade: Wir finden für jede "
            "Immobilie die passende Lösung – abgestimmt auf Ihren Verbrauch "
            "und Ihr Budget."
        ),
        "body_en": (
            "A photovoltaic system is the foundation of your own clean energy "
            "supply. We handle the complete planning — from the first roof "
            "analysis through sizing the modules and inverters to registration "
            "with the grid operator.\n\n"
            "For installation, we rely exclusively on certified specialist "
            "teams and high-quality components. This ensures your system runs "
            "not just reliably, but safely for decades to come.\n\n"
            "Whether pitched roof, flat roof, or façade: we find the right "
            "solution for every property — matched to your consumption and "
            "your budget."
        ),
        "body_ar": (
            "نظام الطاقة الشمسية هو الأساس لإمدادك الخاص بطاقة نظيفة. نتولى "
            "التخطيط الكامل – من تحليل السقف الأول، مروراً بتحديد حجم الألواح "
            "والمحوّلات، وصولاً إلى التسجيل لدى مشغّل الشبكة.\n\n"
            "في التركيب، نعتمد حصراً على فرق متخصصة معتمدة ومكوّنات عالية "
            "الجودة. بذلك نضمن أن يعمل نظامك بشكل موثوق وآمن على مدى عقود.\n\n"
            "سواء كان سقفاً مائلاً أو مستوياً أو واجهة: نجد الحل المناسب لكل "
            "عقار – بما يتناسب مع استهلاكك وميزانيتك."
        ),
    },
    2: {
        "body_de": (
            "Ohne Speicher nutzen die meisten Haushalte nur 25–35 % ihres "
            "selbst erzeugten Solarstroms direkt – der Rest fließt tagsüber "
            "ungenutzt ins Netz. Ein Batteriespeicher ändert das: Er speichert "
            "den Überschuss vom Mittag und stellt ihn Ihnen abends und nachts "
            "wieder zur Verfügung.\n\n"
            "Mit einem passend dimensionierten Speicher steigt Ihr "
            "Eigenverbrauch auf bis zu 80 %. Das bedeutet: mehr Unabhängigkeit "
            "von steigenden Strompreisen und weniger Abhängigkeit vom "
            "öffentlichen Netz.\n\n"
            "Die richtige Speichergröße hängt von Ihrem Verbrauch, Ihrer "
            "Anlagengröße und Ihren Gewohnheiten ab. Wir berechnen sie "
            "individuell – lieber realistisch dimensioniert als unnötig "
            "groß.\n\n"
            "Ein Speicher lohnt sich besonders in Kombination mit einer "
            "Wallbox: So laden Sie Ihr E-Auto auch abends mit gespeichertem "
            "Solarstrom, statt teuren Netzstrom zu beziehen.\n\n"
            "Wir verbauen ausschließlich geprüfte Lithium-Speichersysteme "
            "namhafter Hersteller – mit langer Lebensdauer, hoher Sicherheit "
            "und intelligenter Steuerung."
        ),
        "body_en": (
            "Without storage, most households use only 25–35 % of their "
            "self-generated solar power directly — the rest flows unused into "
            "the grid during the day. A battery storage system changes that: "
            "it stores the midday surplus and makes it available again in the "
            "evening and at night.\n\n"
            "With a correctly sized storage system, your self-consumption "
            "rises to up to 80 %. That means more independence from rising "
            "electricity prices and less reliance on the public grid.\n\n"
            "The right storage size depends on your consumption, your system "
            "size, and your habits. We calculate it individually — "
            "realistically sized rather than unnecessarily large.\n\n"
            "A storage system pays off especially in combination with a "
            "wallbox: this way you charge your EV in the evening with stored "
            "solar power instead of drawing expensive grid electricity.\n\n"
            "We install exclusively tested lithium storage systems from "
            "established manufacturers — with a long lifespan, high safety "
            "standards, and intelligent control."
        ),
        "body_ar": (
            "دون بطارية تخزين، تستخدم معظم المنازل 25 إلى 35٪ فقط من طاقتها "
            "الشمسية المنتَجة مباشرة – بينما يتدفق الباقي دون استخدام إلى "
            "الشبكة خلال النهار. تُغيّر بطارية التخزين ذلك: فهي تخزّن الفائض "
            "من منتصف اليوم وتوفّره لك مجدداً في المساء والليل.\n\n"
            "مع بطارية بالحجم المناسب، يرتفع استهلاكك الذاتي إلى ما يصل إلى "
            "80٪. هذا يعني استقلالية أكبر عن ارتفاع أسعار الكهرباء واعتماداً "
            "أقل على الشبكة العامة.\n\n"
            "يعتمد الحجم المناسب للبطارية على استهلاكك وحجم نظامك وعاداتك. "
            "نحسبه لك بشكل فردي – بحجم واقعي بدلاً من حجم أكبر من اللازم.\n\n"
            "تستحق البطارية العناء بشكل خاص عند دمجها مع شاحن سيارة كهربائية "
            "(والبوكس): بهذه الطريقة تشحن سيارتك الكهربائية مساءً بطاقة شمسية "
            "مخزَّنة بدلاً من كهرباء الشبكة المكلفة.\n\n"
            "نركّب حصراً أنظمة تخزين ليثيوم مختبرة من مصنّعين معروفين – بعمر "
            "افتراضي طويل، وأمان عالٍ، وتحكم ذكي."
        ),
    },
    3: {
        "body_de": (
            "Eine Wallbox macht das Laden Ihres Elektroautos so einfach wie "
            "Tanken – nur bequemer: über Nacht in der eigenen Garage oder am "
            "eigenen Stellplatz, ganz ohne Ladesäule suchen.\n\n"
            "In Kombination mit einer Photovoltaik-Anlage laden Sie Ihr E-Auto "
            "mit selbst erzeugtem Solarstrom – deutlich günstiger als an "
            "öffentlichen Ladepunkten und klimafreundlicher als Strom aus dem "
            "Netz.\n\n"
            "Besonders effizient wird es mit einem Batteriespeicher: "
            "Überschüssiger Solarstrom vom Tag lässt sich speichern und "
            "abends zum Laden nutzen, statt ihn ungenutzt ins Netz "
            "einzuspeisen.\n\n"
            "Wir installieren intelligente Wallboxen, die den Ladevorgang "
            "automatisch mit Ihrer Solarproduktion abstimmen – für maximalen "
            "Eigenverbrauch, ohne dass Sie manuell eingreifen müssen.\n\n"
            "Von der Standortprüfung über die elektrische Absicherung bis zur "
            "Inbetriebnahme: Wir übernehmen die komplette Installation nach "
            "aktuellen Sicherheitsstandards."
        ),
        "body_en": (
            "A wallbox makes charging your EV as simple as refueling — only "
            "more convenient: overnight in your own garage or driveway, with "
            "no need to search for a charging station.\n\n"
            "Combined with a photovoltaic system, you charge your EV with "
            "your own solar power — significantly cheaper than public "
            "charging points and more climate-friendly than grid "
            "electricity.\n\n"
            "It becomes especially efficient with a battery storage system: "
            "surplus solar power from the day can be stored and used for "
            "charging in the evening, instead of being fed unused into the "
            "grid.\n\n"
            "We install smart wallboxes that automatically coordinate "
            "charging with your solar production — for maximum "
            "self-consumption without any manual intervention on your "
            "part.\n\n"
            "From site assessment through electrical safety measures to "
            "commissioning: we handle the complete installation to current "
            "safety standards."
        ),
        "body_ar": (
            "يجعل شاحن السيارة الكهربائية (والبوكس) شحن سيارتك بسيطاً مثل "
            "التزوّد بالوقود – بل أكثر راحة: طوال الليل في مرآبك الخاص أو "
            "موقف سيارتك، دون الحاجة للبحث عن محطة شحن.\n\n"
            "بدمجه مع نظام طاقة شمسية، تشحن سيارتك الكهربائية بطاقتك الشمسية "
            "الخاصة – أرخص بكثير من نقاط الشحن العامة وأكثر مراعاة للمناخ من "
            "كهرباء الشبكة.\n\n"
            "يصبح الأمر أكثر كفاءة مع بطارية تخزين: يمكن تخزين فائض الطاقة "
            "الشمسية النهاري واستخدامه للشحن مساءً، بدلاً من ضخّه دون استخدام "
            "إلى الشبكة.\n\n"
            "نركّب وحدات والبوكس ذكية تنسّق عملية الشحن تلقائياً مع إنتاجك "
            "الشمسي – لتحقيق أقصى استهلاك ذاتي دون أي تدخل يدوي منك.\n\n"
            "من فحص الموقع، مروراً بالحماية الكهربائية، وصولاً إلى التشغيل: "
            "نتولى التركيب الكامل وفق أحدث معايير السلامة."
        ),
    },
    4: {
        "body_de": (
            "Auch eine bestehende Solaranlage sollte regelmäßig überprüft "
            "werden – besonders, wenn sie älter ist oder ihre Leistung "
            "nachgelassen hat. Wir prüfen Module, Verkabelung, Wechselrichter "
            "und alle sicherheitsrelevanten Komponenten.\n\n"
            "Nach der Prüfung erhalten Sie einen verständlichen Bericht: Wo "
            "steht Ihre Anlage leistungsmäßig, gibt es Auffälligkeiten, und "
            "was empfehlen wir? So wissen Sie genau, woran Sie sind – ohne "
            "Fachchinesisch.\n\n"
            "Eine regelmäßige Prüfung erkennt Probleme frühzeitig, bevor sie "
            "zu Ertragsausfällen oder größeren Schäden führen."
        ),
        "body_en": (
            "An existing solar system should also be checked regularly — "
            "especially if it's older or its output has declined. We inspect "
            "modules, wiring, inverters, and all safety-relevant "
            "components.\n\n"
            "After the inspection, you receive a clear report: how is your "
            "system performing, are there any issues, and what do we "
            "recommend? So you know exactly where you stand — no technical "
            "jargon.\n\n"
            "A regular inspection catches problems early, before they lead "
            "to lost yield or bigger damage."
        ),
        "body_ar": (
            "ينبغي أيضاً فحص نظام الطاقة الشمسية القائم بانتظام – خاصة إذا "
            "كان قديماً أو تراجع أداؤه. نفحص الألواح والأسلاك والمحوّلات "
            "وجميع المكوّنات المتعلقة بالسلامة.\n\n"
            "بعد الفحص، تحصل على تقرير مفهوم: كيف يؤدي نظامك، وهل هناك أي "
            "ملاحظات، وما الذي نوصي به؟ هكذا تعرف بالضبط أين تقف – دون "
            "مصطلحات تقنية معقّدة.\n\n"
            "يكتشف الفحص المنتظم المشاكل مبكراً، قبل أن تؤدي إلى فقدان "
            "الإنتاج أو أضرار أكبر."
        ),
    },
    5: {
        "body_de": (
            "Solaranlagen sind wartungsarm – aber nicht wartungsfrei. "
            "Regelmäßige, vorbeugende Wartung sichert die volle Leistung und "
            "Lebensdauer Ihrer Anlage über viele Jahre.\n\n"
            "Unser Service umfasst die Reinigung und Sichtprüfung der Module, "
            "die Kontrolle von Verkabelung und Wechselrichter sowie die "
            "Überwachung der Ertragswerte. Bei Auffälligkeiten reagieren wir "
            "schnell.\n\n"
            "Mit einem Wartungsvertrag müssen Sie sich um nichts kümmern: "
            "Wir behalten Ihre Anlage im Blick, damit Sie sich auf die "
            "Erträge verlassen können."
        ),
        "body_en": (
            "Solar systems are low-maintenance — but not maintenance-free. "
            "Regular, preventive maintenance secures your system's full "
            "performance and lifespan for years to come.\n\n"
            "Our service includes cleaning and visual inspection of the "
            "modules, checking wiring and inverters, and monitoring yield "
            "data. If anything looks off, we respond quickly.\n\n"
            "With a maintenance contract, you don't have to worry about "
            "anything: we keep an eye on your system so you can rely on its "
            "output."
        ),
        "body_ar": (
            "أنظمة الطاقة الشمسية قليلة الصيانة – لكنها ليست بلا صيانة. "
            "تضمن الصيانة الدورية والوقائية الأداء الكامل والعمر الافتراضي "
            "الطويل لنظامك على مدى سنوات.\n\n"
            "تشمل خدمتنا تنظيف الألواح وفحصها بصرياً، ومراقبة الأسلاك "
            "والمحوّلات، ومتابعة قيم الإنتاج. عند وجود أي ملاحظات، نتصرف "
            "بسرعة.\n\n"
            "مع عقد صيانة، لا داعي للقلق بشأن أي شيء: نراقب نظامك حتى تتمكن "
            "من الاعتماد على إنتاجه."
        ),
    },
    6: {
        "body_de": (
            "Für Unternehmen bedeutet eine eigene Solaranlage vor allem "
            "eines: planbare, niedrigere Energiekosten über Jahrzehnte – "
            "unabhängig von schwankenden Strompreisen.\n\n"
            "Ob Produktionshalle, Bürogebäude oder Lagerfläche: Wir "
            "analysieren Ihren tatsächlichen Verbrauch und Ihre Lastprofile, "
            "um eine Anlage zu planen, die zu Ihrem Betrieb passt – nicht zu "
            "groß, nicht zu klein.\n\n"
            "Von der ersten Wirtschaftlichkeitsberechnung über Förderung und "
            "Genehmigung bis zur Umsetzung begleiten wir Sie durch das "
            "gesamte Projekt – mit einem Ansprechpartner für alle Fragen."
        ),
        "body_en": (
            "For businesses, a solar system means one thing above all: "
            "predictable, lower energy costs for decades — independent of "
            "fluctuating electricity prices.\n\n"
            "Whether production hall, office building, or warehouse: we "
            "analyze your actual consumption and load profiles to plan a "
            "system that fits your business — not too big, not too "
            "small.\n\n"
            "From the first feasibility calculation through funding and "
            "permits to implementation, we guide you through the entire "
            "project — with a single point of contact for all questions."
        ),
        "body_ar": (
            "بالنسبة للشركات، يعني نظام الطاقة الشمسية الخاص شيئاً واحداً "
            "قبل كل شيء: تكاليف طاقة أقل ويمكن التخطيط لها على مدى عقود – "
            "بمعزل عن تقلبات أسعار الكهرباء.\n\n"
            "سواء كانت منشأة إنتاج، مبنى مكاتب، أو مساحة تخزين: نحلّل "
            "استهلاكك الفعلي وأنماط الحمل لديك لتخطيط نظام يناسب منشأتك – "
            "ليس كبيراً جداً وليس صغيراً جداً.\n\n"
            "من أول حساب للجدوى الاقتصادية، مروراً بالدعم والتصاريح، وصولاً "
            "إلى التنفيذ: نرافقك خلال المشروع بأكمله – مع جهة تواصل واحدة "
            "لجميع أسئلتك."
        ),
    },
}


def populate_body(apps, schema_editor):
    Service = apps.get_model("catalog", "Service")
    for pk, data in BODY_CONTENT.items():
        Service.objects.filter(pk=pk).update(**data)


def clear_body(apps, schema_editor):
    Service = apps.get_model("catalog", "Service")
    Service.objects.all().update(body_de="", body_en="", body_ar="")


class Migration(migrations.Migration):

    dependencies = [
        (
            "catalog",
            "0005_service_body_ar_service_body_de_service_body_en",
        ),
    ]

    operations = [
        migrations.RunPython(populate_body, clear_body),
    ]
