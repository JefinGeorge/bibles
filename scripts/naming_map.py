"""Naming rules for converting bible XML filenames to the unified JSON naming scheme:

    {language code}_{Language name}_{Version}[_{year}].json

Language codes are ISO 639-1 (two letters) where one exists; languages without a
two-letter code use their ISO 639-3 code (three letters). Version defaults to
"Bible" when the source gives no version designation.
"""
import re

# Files discarded as duplicate versions (kept file -> reason documented).
DISCARD = {
    "EnglishAmplifiedBible.xml": "identical verse text to 'Amplified Bible (1965).xml'",
    "Bengali Bible.xml": "identical verse text to 'BengaliBSIBible.xml' (BSI 2016 O.V.)",
    "ChinTedimBible.xml": "identical verse text to 'ChinTB77Bible.xml' (Tedim Bible 1977)",
    "SongeBible.xml": "mislabeled copy of 'KimiiruBible.xml' (same content and native title 'NTETO INJEGA')",
    "Lithuanian2012KANBible.xml": "identical verse text to 'Lithuanian2012EKUBible.xml'",
    "ChibembaBible.xml": "same 2015 Bible Society of Zambia translation as 'BembaBible.xml' (only verse-boundary shifts differ)",
    "Holy Bible Revised Version (1885).xml": "same English Revised Version as 'Revised Version (1881-1885).xml' (one split verse differs)",
    "EnglishHCSBBible.xml": "same HCSB 2004 text as 'Holman Christian Standard Bible (2004).xml' (1 of 31102 verses differs)",
    "EnglishNRSVBible.xml": "same NRSV 1989 text as 'New Revised Standard Version (1989).xml' (17 of 31103 verses differ)",
    "EnglishNASBBible.xml": "same NASB 1995 translation as 'New American Standard Bible (1995).xml' (digitization variants only)",
    "EnglishNETBible.xml": "same NET 2005 translation as 'New English Translation (2005).xml' (digitization variants only)",
    "EnglishYLTBible.xml": "same YLT 1898 translation as 'Young's Literal Translation (1898).xml' (digitization variants only)",
    "Tamil Bible.xml": "same translation as 'TamilBible.xml' (12 of 31102 verses differ)",
    "The Darby Bible (1890).xml": "same Darby 1890 translation as 'EnglishDarbyBible.xml', which is the more complete copy (65 more verses)",
}

# Human-named source files, curated directly: file -> (code, Language, Version, year or None)
CURATED = {
    "21st Century KJV.xml": ("en", "English", "KJ21", None),
    "A Conservative Version.xml": ("en", "English", "ACV", None),
    "American King James Version (1999).xml": ("en", "English", "AKJV", 1999),
    "American Standard Version (1901).xml": ("en", "English", "ASV", 1901),
    "Amplified Bible (1965).xml": ("en", "English", "AMP", 1965),
    "Apostles' Bible Complete (2004).xml": ("en", "English", "APB", 2004),
    "Bible in Basic English (1964).xml": ("en", "English", "BBE", 1964),
    "Bishop's Bible.xml": ("en", "English", "Bishops", None),
    "Brenton's English Septuagint.xml": ("en", "English", "BrentonLXX", None),
    "Complementary English Version (1995).xml": ("en", "English", "CEV", 1995),
    "Coverdale Bible (1535).xml": ("en", "English", "Coverdale", 1535),
    "Easy to Read Revised Version (2005).xml": ("en", "English", "ERV", 2005),
    "English Jubilee 2000 Bible (2000).xml": ("en", "English", "JUB", 2000),
    # Romanised (Latin-script) Telugu text of the BSI Old Version, despite the filename.
    "English Lo Parishuddha Grandham.xml": ("te", "Telugu", "Romanised", None),
    "English Standard Version (2001).xml": ("en", "English", "ESV", 2001),
    "Geneva Bible (1599).xml": ("en", "English", "Geneva", 1599),
    "Hebrew Names Version.xml": ("en", "English", "HNV", None),
    "Holman Christian Standard Bible (2004).xml": ("en", "English", "HCSB", 2004),
    "King James Version (1769).xml": ("en", "English", "KJV", 1769),
    "Literal Translation of Holy Bible (2000).xml": ("en", "English", "LITV", 2000),
    "Modern King James Version (1962).xml": ("en", "English", "MKJV", 1962),
    "New American Standard Bible (1995).xml": ("en", "English", "NASB", 1995),
    "New Century Version (1991).xml": ("en", "English", "NCV", 1991),
    "New English Translation (2005).xml": ("en", "English", "NET", 2005),
    "New International Reader's Version (1998).xml": ("en", "English", "NIRV", 1998),
    "New International Version (1984) (US).xml": ("en", "English", "NIV", 1984),
    "New International Version (UK).xml": ("en", "English", "NIVUK", None),
    "New King James Version (1982).xml": ("en", "English", "NKJV", 1982),
    "New Life Version (1969).xml": ("en", "English", "NLV", 1969),
    "New Living Translation (1996).xml": ("en", "English", "NLT", 1996),
    "New Revised Standard Version (1989).xml": ("en", "English", "NRSV", 1989),
    "Restored Name KJV.xml": ("en", "English", "RNKJV", None),
    "Revised Standard Version (1952).xml": ("en", "English", "RSV", 1952),
    "Revised Version (1881-1885).xml": ("en", "English", "RV", 1885),
    "Revised Webster Update (1995).xml": ("en", "English", "RWebster", 1995),
    "Rotherhams Emphasized Bible (1902).xml": ("en", "English", "Rotherham", 1902),
    "Telugu Bible (BSI).xml": ("te", "Telugu", "BSI", None),
    "Telugu Bible (WBTC).xml": ("te", "Telugu", "WBTC", None),
    "The Complete Jewish Bible (1998).xml": ("en", "English", "CJB", 1998),
    "The Darby Bible (1890).xml": ("en", "English", "Darby", 1890),
    "The Douay-Rheims American Bible (1899).xml": ("en", "English", "DRA", 1899),
    "The Message Bible (2002).xml": ("en", "English", "MSG", 2002),
    "The Webster Bible (1833).xml": ("en", "English", "Webster", 1833),
    "Third Millennium Bible (1998).xml": ("en", "English", "TMB", 1998),
    "Today's English Version (Good News Bible) (1992).xml": ("en", "English", "TEV", 1992),
    "Today's New International Version (2005).xml": ("en", "English", "TNIV", 2005),
    "Tyndale Bible (1534).xml": ("en", "English", "Tyndale", 1534),
    "Tyndale-Rogers-Coverdale-Cranmer Bible (1537).xml": ("en", "English", "TRCC", 1537),
    "Updated Bible (2006).xml": ("en", "English", "UPDV", 2006),
    "Voice In Wilderness (2006).xml": ("en", "English", "VW", 2006),
    "Wycliffe Bible (1395).xml": ("en", "English", "Wycliffe", 1395),
    "Young's Literal Translation (1898).xml": ("en", "English", "YLT", 1898),
}

# Language prefix (leading title-case words of the camel-case filename) -> (code, Language).
# Longest matching prefix wins; remaining tokens become the version designation.
LANG = {
    "Aceh": ("ace", "Acehnese"),
    "AdilabadGondi": ("gno", "AdilabadGondi"),
    "Afrikaans": ("af", "Afrikaans"),
    "Ahirani": ("ahr", "Ahirani"),
    "Albanian": ("sq", "Albanian"),
    "Amharic": ("am", "Amharic"),
    "AmharicDawro": ("dwr", "Dawro"),
    "AmharicGamo": ("gmv", "Gamo"),
    "AmharicGofa": ("gof", "Gofa"),
    "AmharicTigrinya": ("ti", "Tigrinya"),
    "Arabic": ("ar", "Arabic"),
    "ArabicAlgeria": ("arq", "AlgerianArabic"),
    "ArabicLebanese": ("apc", "LebaneseArabic"),
    "ArabicMorocco": ("ary", "MoroccanArabic"),
    "ArabicTunisian": ("aeb", "TunisianArabic"),
    "Aramaic": ("syc", "Aramaic"),
    "Armenian": ("hy", "Armenian"),
    "Assamese": ("as", "Assamese"),
    "Avar": ("av", "Avar"),
    "Awadhi": ("awa", "Awadhi"),
    "Aymara": ("ay", "Aymara"),
    "Azerbaijan": ("az", "Azerbaijani"),
    "AzerbaijanSouth": ("azb", "SouthAzerbaijani"),
    "Bagri": ("bgq", "Bagri"),
    "Balinese": ("ban", "Balinese"),
    "Balochi": ("bal", "Balochi"),
    "BalochiSoutheren": ("bcc", "SouthernBalochi"),
    "Baoule": ("bci", "Baoule"),
    "Bashkir": ("ba", "Bashkir"),
    "Basque": ("eu", "Basque"),
    "Bavarian": ("bar", "Bavarian"),
    "Belarusian": ("be", "Belarusian"),
    "Bemba": ("bem", "Bemba"),
    "Bengali": ("bn", "Bengali"),
    "Berber": ("shi", "Tachelhit"),
    "Bhilali": ("bhi", "Bhilali"),
    "Bodo": ("brx", "Bodo"),
    "Bosnian": ("bs", "Bosnian"),
    "Braj": ("bra", "Braj"),
    "Bugis": ("bug", "Buginese"),
    "Bulgarian": ("bg", "Bulgarian"),
    "Bundeli": ("bns", "Bundeli"),
    "Burmese": ("my", "Burmese"),
    "Catalan": ("ca", "Catalan"),
    "Cebuano": ("ceb", "Cebuano"),
    "Chechen": ("ce", "Chechen"),
    "Chewa": ("ny", "Chichewa"),
    "Chhattisgarhi": ("hne", "Chhattisgarhi"),
    "Chibemba": ("bem", "Bemba"),
    "Chin": ("cnh", "Chin"),  # per-file overrides below give each Chin bible its language
    "ChinMatupi": ("hlt", "MatuChin"),
    "ChinTedim": ("ctd", "TedimChin"),
    "Chinese": ("zh", "Chinese"),
    "ChineseWenli": ("lzh", "LiteraryChinese"),
    "Chuvash": ("cv", "Chuvash"),
    "Coptic": ("cop", "Coptic"),
    "Croatian": ("hr", "Croatian"),
    "Czech": ("cs", "Czech"),
    "Dagbani": ("dag", "Dagbani"),
    "Danish": ("da", "Danish"),
    "Dinka": ("din", "Dinka"),
    "Dogri": ("doi", "Dogri"),
    "Dutch": ("nl", "Dutch"),
    "DutchFrisian": ("fy", "Frisian"),
    "Dyula": ("dyu", "Dyula"),
    "Edo": ("bin", "Edo"),
    "English": ("en", "English"),
    "Esperanto": ("eo", "Esperanto"),
    "Estonian": ("et", "Estonian"),
    "Ewe": ("ee", "Ewe"),
    "Finnish": ("fi", "Finnish"),
    "Fon": ("fon", "Fon"),
    "French": ("fr", "French"),
    "Fulfulde": ("ff", "Fulfulde"),
    "Gaelic": ("gd", "ScottishGaelic"),
    "Galacian": ("gl", "Galician"),
    "Garhwali": ("gbm", "Garhwali"),
    "Georgian": ("ka", "Georgian"),
    "German": ("de", "German"),
    "Ghomala": ("bbj", "Ghomala"),
    "Greek": ("el", "Greek"),  # ancient-text editions overridden to grc below
    "Guarani": ("gn", "Guarani"),
    "Gujarati": ("gu", "Gujarati"),
    "Gussi": ("guz", "Gusii"),
    "Hadiyya": ("hdy", "Hadiyya"),
    "Haitian": ("ht", "HaitianCreole"),
    "Haryanvi": ("bgc", "Haryanvi"),
    "Hausa": ("ha", "Hausa"),
    "Hebrew": ("he", "Hebrew"),
    "Hindi": ("hi", "Hindi"),
    "HindiFiji": ("hif", "FijiHindi"),
    "Hmong": ("hmn", "Hmong"),
    "Hungarian": ("hu", "Hungarian"),
    "Iban": ("iba", "Iban"),
    "Ibibio": ("ibb", "Ibibio"),
    "Icelandic": ("is", "Icelandic"),
    "Igbo": ("ig", "Igbo"),
    "Ika": ("ikk", "Ika"),
    "Ilokano": ("ilo", "Ilokano"),
    "Ilonggo": ("hil", "Hiligaynon"),
    "Indonesian": ("id", "Indonesian"),
    "Irish": ("ga", "Irish"),
    "Italian": ("it", "Italian"),
    "IuMien": ("ium", "IuMien"),
    "Jamaican": ("jam", "JamaicanCreole"),
    "Japanese": ("ja", "Japanese"),
    "Javanese": ("jv", "Javanese"),
    "Kabardian": ("kbd", "Kabardian"),
    "Kabyle": ("kab", "Kabyle"),
    "Kachin": ("kac", "Kachin"),
    "Kalenjin": ("kln", "Kalenjin"),
    "Kamba": ("kam", "Kamba"),
    "Kangri": ("xnr", "Kangri"),
    "Kannada": ("kn", "Kannada"),
    "Karakalpak": ("kaa", "Karakalpak"),
    "Kazakhstan": ("kk", "Kazakh"),
    "Kenya": ("ki", "Kikuyu"),  # KenyaGIKCLBible is the 2008 Kikuyu bible
    "Khmer": ("km", "Khmer"),
    "Kiche": ("quc", "Kiche"),
    "Kikuyu": ("ki", "Kikuyu"),
    "Kikwango": ("ktu", "Kituba"),  # "Kikwango" is the mission-era name for Kituba
    "Kimbundu": ("kmb", "Kimbundu"),
    "Kimiiru": ("mer", "Meru"),
    "Kinyarwanda": ("rw", "Kinyarwanda"),
    "Kirundi": ("rn", "Kirundi"),
    "Kituba": ("ktu", "Kituba"),
    "Konkani": ("kok", "Konkani"),
    "Korean": ("ko", "Korean"),
    "Koya": ("kff", "Koya"),
    "Krio": ("kri", "Krio"),
    "Kumaoni": ("kfy", "Kumaoni"),
    "Kurdish": ("ku", "Kurdish"),  # per-file overrides pick kmr/ckb/sdh
    "Kurukh": ("kru", "Kurukh"),
    "Kyrgyz": ("ky", "Kyrgyz"),
    "Lahu": ("lhu", "Lahu"),
    "Lambadi": ("lmn", "Lambadi"),
    "Lango": ("laj", "Lango"),
    "Lao": ("lo", "Lao"),
    "Latin": ("la", "Latin"),
    "Latvian": ("lv", "Latvian"),
    "LiberianKreyol": ("lir", "LiberianKreyol"),
    "Lingala": ("ln", "Lingala"),
    "Lithuanian": ("lt", "Lithuanian"),
    "Lomwe": ("ngl", "Lomwe"),
    "Luganda": ("lg", "Luganda"),
    "Lugbara": ("lgg", "Lugbara"),
    "Luguru": ("ruf", "Luguru"),
    "Luo": ("luo", "Luo"),
    "Maasai": ("mas", "Maasai"),
    "Macedonian": ("mk", "Macedonian"),
    "Madurese": ("mad", "Madurese"),
    "Maithili": ("mai", "Maithili"),
    "Makhuwa": ("vmw", "Makhuwa"),
    "Makonde": ("kde", "Makonde"),
    "Malagasy": ("mg", "Malagasy"),
    "Malayalam": ("ml", "Malayalam"),
    "Malaysian": ("ms", "Malay"),
    "Maori": ("mi", "Maori"),
    "Marathi": ("mr", "Marathi"),
    "Marwari": ("mwr", "Marwari"),
    "Mazanderani": ("mzn", "Mazanderani"),
    "Meitei": ("mni", "Meitei"),
    "Mende": ("men", "Mende"),
    "Mewari": ("mtr", "Mewari"),
    "Mizo": ("lus", "Mizo"),
    "Moba": ("mfq", "Moba"),
    "Moldovian": ("ro", "Moldovan"),
    "Mongolian": ("mn", "Mongolian"),
    "Morisyen": ("mfe", "Morisyen"),
    "Mossi": ("mos", "Mossi"),
    "Munda": ("unr", "Mundari"),
    "Nahuatl": ("nah", "Nahuatl"),  # variant codes overridden per file below
    "Ndau": ("ndc", "Ndau"),
    "Ndebele": ("nd", "Ndebele"),
    "Nepali": ("ne", "Nepali"),
    "NepaliTamang": ("taj", "Tamang"),
    "NewAmerican": ("en", "English"),
    "NigerianPidgin": ("pcm", "NigerianPidgin"),
    "Norwegian": ("no", "Norwegian"),
    "Nuer": ("nus", "Nuer"),
    "Nyankole": ("nyn", "Nyankole"),
    "Odia": ("or", "Odia"),
    "OriginalGreek": ("grc", "AncientGreek"),
    "OriginalHebrew": ("hbo", "AncientHebrew"),
    "Oromo": ("om", "Oromo"),
    "Pampanga": ("pam", "Kapampangan"),
    "PapuaNewGuinea": ("tpi", "TokPisin"),
    "PapuaNewGuineaTokPisin": ("tpi", "TokPisin"),
    "Pashto": ("ps", "Pashto"),
    "Persian": ("fa", "Persian"),
    "PersianDari": ("prs", "Dari"),
    "Polish": ("pl", "Polish"),
    "Portuguese": ("pt", "Portuguese"),
    "Pular": ("fuf", "Pular"),
    "Punjabi": ("pa", "Punjabi"),
    "Qeqchi": ("kek", "Qeqchi"),
    "Quechuan": ("qu", "Quechua"),  # variant codes overridden per file below
    "Romani": ("rom", "Romani"),
    "Romanian": ("ro", "Romanian"),
    "Russian": ("ru", "Russian"),
    "Sadri": ("sck", "Sadri"),
    "Sanskrit": ("sa", "Sanskrit"),
    "Santali": ("sat", "Santali"),
    "Sasak": ("sas", "Sasak"),
    "Sena": ("seh", "Sena"),
    "SenaMalawi": ("swk", "MalawiSena"),
    "Seraiki": ("skr", "Saraiki"),
    "Serbian": ("sr", "Serbian"),
    "Shan": ("shn", "Shan"),
    "Shekhawati": ("swv", "Shekhawati"),
    "Shilluk": ("shk", "Shilluk"),
    "Shona": ("sn", "Shona"),
    "Sidamo": ("sid", "Sidamo"),
    "Sindhi": ("sd", "Sindhi"),
    "Sinhala": ("si", "Sinhala"),
    "Siswati": ("ss", "Swati"),
    "Slovakian": ("sk", "Slovak"),
    "SlovakianRomani": ("rmc", "CarpathianRomani"),
    "Slovenian": ("sl", "Slovenian"),
    "Soga": ("xog", "Soga"),
    "Somalian": ("so", "Somali"),
    "Songe": ("sop", "Songe"),
    "Sotho": ("st", "SouthernSotho"),
    "Spanish": ("es", "Spanish"),
    "Sukuma": ("suk", "Sukuma"),
    "Sundanese": ("su", "Sundanese"),
    "Swahili": ("sw", "Swahili"),
    "Swedish": ("sv", "Swedish"),
    "Sylheti": ("syl", "Sylheti"),
    "Tagalog": ("tl", "Tagalog"),
    "Tajik": ("tg", "Tajik"),
    "Tamasheq": ("taq", "Tamasheq"),
    "Tamil": ("ta", "Tamil"),
    "Tarifit": ("rif", "Tarifit"),
    "Tashelhayt": ("shi", "Tachelhit"),
    "Tatar": ("tt", "Tatar"),
    "Telugu": ("te", "Telugu"),
    "Teso": ("teo", "Teso"),
    "Thado": ("tcz", "ThadoChin"),
    "Thai": ("th", "Thai"),
    "TheNewJerusalem": ("en", "English"),
    "Tibetian": ("bo", "Tibetan"),
    "Tiv": ("tiv", "Tiv"),
    "Tshiluba": ("lua", "Tshiluba"),
    "Tshivenda": ("ve", "Venda"),
    "Tsonga": ("ts", "Tsonga"),
    "Tswana": ("tn", "Tswana"),
    "Tulu": ("tcy", "Tulu"),
    "Turkana": ("tuv", "Turkana"),
    "Turkish": ("tr", "Turkish"),
    "Turkmen": ("tk", "Turkmen"),
    "Twi": ("tw", "Twi"),
    "Ukrainian": ("uk", "Ukrainian"),
    "Umbundu": ("umb", "Umbundu"),
    "Urdu": ("ur", "Urdu"),
    "Uyghur": ("ug", "Uyghur"),
    "Uzbek": ("uz", "Uzbek"),
    "Vietnamese": ("vi", "Vietnamese"),
    "Waray": ("war", "Waray"),
    "Welsh": ("cy", "Welsh"),
    "Wolaytta": ("wal", "Wolaytta"),
    "Wolof": ("wo", "Wolof"),
    "WorldEnglish": ("en", "English"),
    "Xhosa": ("xh", "Xhosa"),
    "Yoruba": ("yo", "Yoruba"),
    "Zande": ("zne", "Zande"),
    "Zarma": ("dje", "Zarma"),
    "Zulu": ("zu", "Zulu"),
}

# Per-file corrections: any of code/lang/version/year may be given.
# Identifications come from each file's translation metadata (and, for Chin 2010,
# from matching the verse text against the published Zyphe Chin New Testament).
FILE_OVERRIDES = {
    "AramaicBible.xml": {"version": "Peshitta"},
    "Chin2010Bible.xml": {"code": "zyp", "lang": "ZypheChin"},
    "ChinBSIBible.xml": {"code": "mrh", "lang": "MaraChin"},
    "ChinCSHBible.xml": {"code": "csh", "lang": "AshoChin"},
    "ChinDNTBible.xml": {"code": "dao", "lang": "DaaiChin"},
    "ChinKNTPBible.xml": {"code": "anl", "lang": "Khongso"},
    "ChinSCB2Bible.xml": {"code": "csy", "lang": "SizangChin"},
    "ChinTB77Bible.xml": {"code": "ctd", "lang": "TedimChin"},
    "ChinTBR17Bible.xml": {"code": "ctd", "lang": "TedimChin"},
    "ChinTDBBible.xml": {"code": "ctd", "lang": "TedimChin"},
    "Dinka2006Bible.xml": {"code": "dik"},          # Southwestern Dinka per metadata
    "DinkaBible.xml": {"code": "dip"},              # DIP = Northeastern Dinka (DIPBSS 2009)
    "DinkaLEKJOTBible.xml": {"code": "dks"},        # Southeastern Dinka per metadata
    "Fulfulde2010Bible.xml": {"code": "fuv"},       # Caka Nigeria
    "FulfuldeAdamawaBible.xml": {"code": "fub"},
    "FulfuldeAlkawalBible.xml": {"code": "fuq"},    # Central-Eastern Niger
    "FulfuldeArabicBible.xml": {"code": "fuv"},     # Caka Nigeria, Arabic script
    "FulfuldeBeninBible.xml": {"code": "fue"},      # Borgu
    "FulfuldeBurkinaFasoBible.xml": {"code": "fuh"},
    "FulfuldeDewtereBible.xml": {"code": "fuh"},    # Burkina Faso per metadata
    "FulfuldeWestNigerBible.xml": {"code": "fuh"},
    "Greek1550Bible.xml": {"code": "grc", "lang": "AncientGreek", "version": "Stephanus"},
    "GreekBYZ04Bible.xml": {"code": "grc", "lang": "AncientGreek"},
    "GreekBYZ18Bible.xml": {"code": "grc", "lang": "AncientGreek"},
    "GreekElzevirBible.xml": {"code": "grc", "lang": "AncientGreek"},
    "GreekF35Bible.xml": {"code": "grc", "lang": "AncientGreek"},
    "GreekGNTBible.xml": {"code": "grc", "lang": "AncientGreek"},
    "GreekSBLGNTBible.xml": {"code": "grc", "lang": "AncientGreek"},
    "GreekTCGNTBible.xml": {"code": "grc", "lang": "AncientGreek"},
    "GreekTHGNTBible.xml": {"code": "grc", "lang": "AncientGreek"},
    "GreekTR1894Bible.xml": {"code": "grc", "lang": "AncientGreek"},
    "HebrewAleppoCodexBible.xml": {"code": "hbo", "lang": "AncientHebrew", "version": "AleppoCodex"},
    "HebrewLeningradCodexBible.xml": {"code": "hbo", "lang": "AncientHebrew", "version": "LeningradCodex"},
    "KikwangoBible.xml": {"version": "Kikwango"},
    "Kurdish2005Bible.xml": {"code": "kmr", "lang": "Kurmanji"},
    "Kurdish2017Bible.xml": {"code": "kmr", "lang": "Kurmanji", "version": "PNU"},
    "KurdishBHDBible.xml": {"code": "kmr", "lang": "Kurmanji", "version": "Behdini"},
    "KurdishBible.xml": {"code": "ckb", "lang": "Sorani", "version": "KSS"},
    "KurdishKMRNTCBible.xml": {"code": "kmr", "lang": "Kurmanji"},
    "KurdishKMRNTLBible.xml": {"code": "kmr", "lang": "Kurmanji"},
    "KurdishPNTZSBible.xml": {"code": "ckb", "lang": "Sorani"},
    "KurdishSKBBible.xml": {"code": "kmr", "lang": "Kurmanji"},
    "KurdishSKVBible.xml": {"code": "sdh", "lang": "SouthernKurdish"},
    "MalayalamMalovBible.xml": {"version": "OVBSI"},  # metadata: Malayalam OV-BSI 2016
    "HindiBible.xml": {"version": "HHBD"},          # metadata: Hindi HHBD (BSI); distinct from 'Hindi Bible.xml'
    "Nahuatl2012Bible.xml": {"code": "nhi"},        # Zacatlan-Ahuacatlan-Tepetzintla
    "NahuatlGUBible.xml": {"code": "ngu"},          # Guerrero
    "NahuatlNHEBible.xml": {"code": "nhe"},         # Eastern Huasteca
    "Ndebele2012Bible.xml": {"code": "nr"},         # SND = South African IsiNdebele
    "New American Bible.xml": {"version": "NAB"},
    "OriginalGreekBible.xml": {"version": "Original"},
    "OriginalHebrewBible.xml": {"version": "Original"},
    "Quechuan2010Bible.xml": {"code": "qub"},       # QUB = Huallaga
    "QuechuanQVSBible.xml": {"code": "qvs"},        # San Martin
    "QuechuanQVWBible.xml": {"code": "qvw"},        # Huaylla Wanca
    "QuechuanQXOBible.xml": {"code": "qxo"},        # Southern Conchucos
    "RomaniRMCBible.xml": {"code": "rmc", "lang": "CarpathianRomani"},
    "Slovenian2014Bible.xml": {"version": "ZNZ"},   # Živa Nova Zaveza NT
    "SlovenianBible.xml": {"version": "Chraska", "year": 1914},  # Chráskov Prevod, © 1914 BFBS
    "SothoBible.xml": {"code": "nso", "lang": "NorthernSotho", "version": "Sepedi"},
    "The New Jerusalem Bible.xml": {"version": "NJB"},
    "World English Bible.xml": {"version": "WEB"},
}

_YEAR_RE = re.compile(r"\b(1[5-9]\d\d|20[0-2]\d)\b")
_TOKEN_RE = re.compile(r"[A-Z][a-z]+|[A-Z]+(?![a-z])|\d+|[a-z]+|'")


def _tokens(stem):
    return _TOKEN_RE.findall(stem)


def resolve(filename, title_attr=""):
    """Return (code, language, version, year, target_json_name) for a source file."""
    if filename in CURATED:
        code, lang, version, year = CURATED[filename]
    else:
        stem = filename[:-4].replace(" ", "")
        if stem.endswith("Bible"):
            stem = stem[:-5]
        toks = _tokens(stem)
        # longest run of leading title-case words that matches a known language
        lead = []
        for t in toks:
            if re.fullmatch(r"[A-Z][a-z]+", t):
                lead.append(t)
            else:
                break
        match = None
        for i in range(len(lead), 0, -1):
            cand = "".join(lead[:i])
            if cand in LANG:
                match = cand
                break
        if match is None:
            raise KeyError(f"no language mapping for {filename!r}")
        code, lang = LANG[match]
        rest = toks[len(_tokens(match)):]
        # pull a publication year out of the remaining tokens
        year = None
        version_toks = []
        for t in rest:
            if year is None and _YEAR_RE.fullmatch(t):
                year = int(t)
            else:
                version_toks.append(t)
        version = "".join(v for v in version_toks if v != "'")
        # fall back to a single unambiguous year in the title metadata
        if year is None and title_attr:
            found = set(_YEAR_RE.findall(title_attr))
            if len(found) == 1:
                year = int(found.pop())

    ov = FILE_OVERRIDES.get(filename, {})
    code = ov.get("code", code)
    lang = ov.get("lang", lang)
    version = ov.get("version", version)
    year = ov.get("year", year)
    if not version:
        version = "Bible"
    target = f"{code}_{lang}_{version}" + (f"_{year}" if year else "") + ".json"
    return code, lang, version, year, target
