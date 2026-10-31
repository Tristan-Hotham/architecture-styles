"""Style families: the hand-checked mapping from Wikidata architectural styles (P149 values) to readable families.

Order of rules for each style:
  1. HAND: an explicit, hand-checked decision for every style used by 20 or more buildings (and some smaller ones).
  2. KEYWORDS: words in the English label (for the long tail).
  3. ANCESTOR: the nearest ancestor (P279 subclass of, P361 part of) that has a family from rules 1 or 2.
  4. Otherwise 'other'.
A style is a 'revival' when it re-uses an earlier style's forms in a later period (Gothic Revival, Greek Revival,
Moorish Revival, Colonial Revival ...). Revival styles keep the family of the style they revive and carry the flag.
The full result for all 1,326 styles is published as data/style_families.csv.
"""
import re

# key, name, colour, one-line description
FAMILIES = [
    ("ancient", "Ancient", "#8C6A3F", "Egyptian, Greek, Roman, Persian and other ancient building"),
    ("byzantine", "Byzantine and Orthodox", "#C99A2E", "Byzantine, Armenian, Georgian and Old Russian, with their revivals"),
    ("romanesque", "Romanesque", "#B5553A", "Pre-Romanesque, Romanesque and Norman, with Romanesque Revival"),
    ("gothic", "Gothic", "#283B7A", "Gothic in all its regional forms, with Gothic Revival"),
    ("renaissance", "Renaissance", "#2F8C74", "Renaissance and Mannerist, with Renaissance Revival and Italianate"),
    ("baroque", "Baroque and Rococo", "#A3214A", "Baroque and Rococo, with baroque revival"),
    ("neoclassical", "Neoclassical", "#5E86C1", "Classicism, Palladian, Georgian, Federal, Empire and Greek Revival"),
    ("historicist", "Historicist and eclectic", "#9C7CC4", "Eclectic, Victorian, Beaux-Arts, Second Empire and Queen Anne"),
    ("colonial", "Colonial", "#D9A35B", "Colonial building in the Americas and elsewhere, with Colonial and Spanish Colonial Revival"),
    ("crafts", "Arts and Crafts and romantic", "#7C9A2E", "Arts and Crafts, Craftsman, Prairie School, rustic and National Romantic"),
    ("nouveau", "Art Nouveau", "#3AAFB9", "Art Nouveau, Jugendstil, Secession and Catalan modernisme"),
    ("deco", "Art Deco", "#E2B007", "Art Deco, Moderne and Streamline Moderne"),
    ("modern", "Modernist", "#33363D", "Modern, functionalist, rationalist, International Style, constructivist and Bauhaus"),
    ("brutalist", "Brutalist", "#8C8F94", "Brutalist architecture"),
    ("postmodern", "Postmodern and contemporary", "#E0608A", "Postmodern, high-tech, deconstructivist and contemporary"),
    ("islamic", "Islamic", "#1E7A4A", "Arab, Andalusian, Maghrebi, Mamluk and Mudéjar, with Moorish Revival"),
    ("persian", "Persian", "#1F6FB2", "Iranian architecture by dynasty: Seljuk, Ilkhanid, Timurid, Safavid, Qajar, Pahlavi"),
    ("ottoman", "Ottoman", "#7A2E2A", "Ottoman architecture"),
    ("mughal", "Mughal and Indo-Islamic", "#E8743B", "Indo-Islamic and Mughal, with Indo-Saracenic"),
    ("hindu", "Hindu temple", "#F2A31B", "Dravidian, Nagara, Kalinga and Bengal temple styles"),
    ("chinese", "Chinese and Korean", "#D1342F", "Chinese and Korean architecture"),
    ("japanese", "Japanese", "#6A3D9A", "Shinto shrine styles, Buddhist temple styles, kofun and minka"),
    ("seasian", "Southeast Asian", "#A0522D", "Khmer, Thai, Javanese, Balinese and Malay"),
    ("precolumbian", "Pre-Columbian", "#8E7A12", "Maya, Inca and other Pre-Columbian building, with Mayan Revival"),
    ("vernacular", "Vernacular", "#B39A68", "Vernacular, folk, wooden and timber-framed building"),
    ("other", "Other or general", "#BDB6AA", "General or technical labels: medieval, industrial, roof shapes, orders"),
]
FKEYS = [f[0] for f in FAMILIES]

# Hand-checked decisions: QID -> (family, revival, English label as checked). Every style used by 20 or more
# buildings in the data is listed here; the label is only a reminder (the QID is what is matched).
HAND = {}


def _h(fam, rev, *pairs):
    for q, lab in pairs:
        HAND[q] = (fam, rev, lab)


_h("vernacular", False, ("Q930314", "vernacular architecture"), ("Q12033488", "vernacular architecture in the Czech Republic"),
   ("Q13031741", "vernacular architecture of Belarus"), ("Q4426604", "wooden architecture"), ("Q1153484", "folk art"),
   ("Q12020836", "timber-framed house"), ("Q96069702", "Hungarian folk style"), ("Q27055630", "Russian wooden architecture"),
   ("Q5967732", "I-house"), ("Q19347338", "Architectural school of Western Paliessie"), ("Q19347339", "Architectural school of Eastern Paliessie"),
   ("Q11327340", "half-timbering"), ("Q629000", "timber framing"), ("Q85685942", "traditional (architectural style)"),
   ("Q5477607", "Zakopane Style architecture"), ("Q12275767", "The Architecture of the Bulgarian Revival"), ("Q1004004", "Bulgarian National Revival"),
   ("Q2611710", "cottage style"), ("Q5175548", "cottage orné"), ("Q63982693", "styl dworkowy"), ("Q58621850", "dalan"),
   ("Q4069878", "Arran architectural school"), ("Q4314692", "Architectural school of Nakhchivan"), ("Q16414661", "Shirvan-Absheron architectural school"),
   ("Q489021", "Sudano-Sahelian architecture"), ("Q12961919", "bahay na bato"), ("Q98939712", "Boom Town style"), ("Q7080212", "saltbox"),
   ("Q16911022", "Folk Victorian"), ("Q850107", "bungalow"), ("Q3347108", "Neo-Basque style"), ("Q11587139", "rock-cut architecture"),
   ("Q2748473", "Asturian architecture"), ("Q7703756", "Territorial architecture"))
_h("other", False, ("Q1349760", "medieval architecture"), ("Q1477476", "industrial architecture"), ("Q900557", "cast-iron architecture"),
   ("Q855025", "East Asian hip-and-gable roof"), ("Q149617", "gable roof"), ("Q162034", "hip roof"), ("Q192664", "Doric order"),
   ("Q189548", "Ionic order"), ("Q47848", "sacred architecture"), ("Q1016889", "Burr Truss"), ("Q1328068", "truss"), ("Q11303", "skyscraper"),
   ("Q12797", "star fort"), ("Q1788398", "cross-in-square"), ("Q1936626", "aisleless church"), ("Q728266", "hall church"), ("Q744296", "wooden church"),
   ("Q2710172", "transitional architecture"), ("Q7166434", "pepperpot"), ("Q3389223", "piscine Tournesol"), ("Q548879", "novelty architecture"),
   ("Q3282723", "reconstruction-period architecture"), ("Q2600188", "Russian architecture"), ("Q4520962", "tented-roof church"),
   ("Q7209882", "Polish Cathedral style"), ("Q867703", "Western-style building"), ("Q37068", "Romanticism"), ("Q10857409", "realism"),
   ("Q49974793", "Neotraditional"), ("Q115920141", "Gruppenbau"), ("Q2864737", "sacred architecture"), ("Q12271", "architecture"),
   ("Q1501585", "architecture of Iran"), ("Q102932", "avant-garde"), ("Q3389209", "(unlabelled, France, 1972)"),
   ("Q3501272", "(unlabelled)"), ("Q56378393", "(unlabelled)"),
   ("Q125472971", "(unlabelled: Spanish national grain silo type)"), ("Q125472998", "(unlabelled: Spanish national granary type)"),
   ("Q125473228", "(unlabelled: Spanish grain silo type)"), ("Q125472980", "(unlabelled: Spanish grain silo type)"),
   ("Q125472936", "(unlabelled: Spanish grain silo type)"), ("Q125473136", "(unlabelled: Spanish grain silo type)"),
   ("Q125473115", "(unlabelled: Spanish grain silo type)"), ("Q125472950", "(unlabelled: Spanish grain silo type)"),
   ("Q125472717", "(unlabelled: Spanish grain silo type)"), ("Q125473013", "(unlabelled: Spanish grain silo type)"),
   ("Q125473090", "(unlabelled: Spanish grain silo type)"), ("Q125473009", "(unlabelled: Spanish grain silo type)"),
   ("Q125473222", "(unlabelled: Spanish grain silo type)"))
_h("ancient", False, ("Q223750", "ancient Roman architecture"), ("Q331273", "ancient Greek architecture"), ("Q3844828", "Sasanian architecture"),
   ("Q4673399", "Achaemenid architecture"), ("Q2011484", "Hellenistic architecture"), ("Q17993889", "Parthian architecture"),
   ("Q842352", "ancient Egyptian architecture"), ("Q1008014", "Greco-Buddhist art"))
_h("byzantine", False, ("Q47591", "Byzantine architecture"), ("Q2860299", "Armenian architecture"), ("Q16148493", "Armenian church architecture"),
   ("Q2494008", "Early Christian architecture"), ("Q429811", "early Christian art"), ("Q38451143", "Pskov architectural style"),
   ("Q112869097", "Yaroslavl school"), ("Q4401046", "Uzorochye"), ("Q2561822", "Coptic architecture"), ("Q1810654", "Serbo-Byzantine architecture"),
   ("Q211884", "Byzantine art"), ("Q2860335", "architecture of Georgia"), ("Q460596", "Brâncovenesc art"))
_h("byzantine", True, ("Q2026876", "Russian Revival architecture"), ("Q966571", "Byzantine Revival architecture"), ("Q2860359", "Russian-Byzantine architecture"),
   ("Q106225044", "Neo-Byzantine architecture in the Russian Empire"), ("Q3501300", "Serbo-Byzantine style (modern architecture)"),
   ("Q12720948", "Romanian Revival architecture"))
_h("romanesque", False, ("Q46261", "Romanesque architecture"), ("Q46805", "Romanesque art"), ("Q136693", "Norman architecture"),
   ("Q708807", "pre-Romanesque art"), ("Q2722661", "First Romanesque"), ("Q9159129", "Pre-Romanesque architecture"), ("Q537454", "Anglo-Saxon architecture"),
   ("Q2864731", "Romanesque art of Provence"), ("Q2884586", "romanesque architecture in Italy"), ("Q7362467", "Romanesque architecture in Spain"),
   ("Q3940633", "romanesque arte in Pisa"), ("Q10412776", "Visigothic architecture"), ("Q963612", "Romanesque architecture in Sardinia"),
   ("Q1334868", "Romanesque art in Catalonia"), ("Q2337737", "Carolingian architecture"), ("Q3940635", "Romanesque art in Apulia"),
   ("Q2083873", "Lombard architecture"), ("Q9159154", "Romanesque architecture in Poland"), ("Q2860289", "Norman architecture of Sicily"),
   ("Q1973348", "Norman-Arab-Byzantine culture"))
_h("romanesque", True, ("Q744373", "Romanesque Revival architecture"), ("Q3501297", "Richardsonian Romanesque"), ("Q1755128", "Rundbogenstil"))
_h("gothic", False, ("Q176483", "Gothic architecture"), ("Q46825", "Gothic art"), ("Q10924220", "Late Gothic"), ("Q695863", "Brick Gothic"),
   ("Q750752", "English Gothic architecture"), ("Q867769", "International Gothic"), ("Q1351624", "Flamboyant"), ("Q751878", "Manueline"),
   ("Q33247990", "Early Gothic architecture"), ("Q2245489", "Italian Gothic architecture"), ("Q21032839", "Valencian Gothic"),
   ("Q2864605", "Cistercian architecture"), ("Q2704973", "Spanish Gothic architecture"), ("Q2602891", "Isabelline"), ("Q7919731", "Venetian Gothic architecture"),
   ("Q3111491", "Meridional Gothic"), ("Q956832", "Brabantine Gothic"), ("Q2245347", "French Gothic architecture"), ("Q4895430", "Catalan Gothic"),
   ("Q1896616", "Romano-Gothic"), ("Q15609295", "Perpendicular Gothic"), ("Q16862908", "Belarusian Gothic"), ("Q1962333", "Gothic Survival architecture"),
   ("Q72553961", "classic gothic"), ("Q509364", "Tudor architecture"))
_h("gothic", True, ("Q186363", "Gothic Revival"), ("Q4365410", "Carpenter Gothic"), ("Q5757358", "High Victorian Gothic"), ("Q942123", "Russian pseudo-gothic"),
   ("Q56266198", "Collegiate Gothic"), ("Q3476363", "Scottish baronial architecture"), ("Q24265256", "Maximilianstil"), ("Q7851317", "Tudor Revival architecture"),
   ("Q2056895", "Neo-Manueline"), ("Q111679105", "English Cottage architecture"))
_h("renaissance", False, ("Q236122", "Renaissance architecture"), ("Q4692", "Renaissance"), ("Q131808", "Mannerism"), ("Q1114972", "Mannerist architecture"),
   ("Q3399545", "Spanish Renaissance architecture"), ("Q577852", "Plateresque"), ("Q2860343", "Jacobean architecture"), ("Q6297212", "French Renaissance architecture"),
   ("Q1404472", "Italian Renaissance"), ("Q1614189", "Herrerian"), ("Q2365000", "Elizabethan architecture"), ("Q9159144", "Italian Renaissance architecture"),
   ("Q1472236", "Early Renaissance"), ("Q2406030", "Mosan renaissance style"), ("Q610877", "Northern Renaissance"), ("Q2455000", "German Renaissance"),
   ("Q430167", "Spanish Renaissance"), ("Q1133779", "Renaissance art"))
_h("renaissance", True, ("Q502163", "Renaissance Revival architecture"), ("Q615196", "Italianate architecture"), ("Q6119627", "Jacobethan"),
   ("Q5118885", "châteauesque"), ("Q3347056", "Flemish Renaissance Revival architecture"), ("Q2269431", "Semper Nicolai school"),
   ("Q5705254", "Neo-Plateresque architecture"))
_h("baroque", False, ("Q840829", "baroque architecture"), ("Q37853", "Baroque"), ("Q64334168", "Late Baroque"), ("Q122960", "Rococo"),
   ("Q11350230", "Rococo architecture"), ("Q6092662", "Italian Baroque architecture"), ("Q1542287", "Ukrainian Baroque"), ("Q7573157", "Spanish Baroque architecture"),
   ("Q109180294", "Early Baroque"), ("Q1141784", "Sicilian Baroque"), ("Q2574110", "English Baroque"), ("Q1323065", "Louis XIII style"),
   ("Q3635094", "Russian Baroque"), ("Q5249786", "New Spanish Baroque"), ("Q1003339", "classicist baroque"), ("Q13107150", "Czech Baroque architecture"),
   ("Q2300756", "Dutch Baroque architecture"), ("Q945693", "Louis Quinze"), ("Q19910996", "Moscow baroque"), ("Q2568026", "Vilnian Baroque"),
   ("Q616753", "Naryshkin Baroque"), ("Q2636415", "Petrine Baroque"), ("Q4418329", "Siberian Baroque"), ("Q1517921", "Louis XIV style"),
   ("Q2420087", "Neapolitan baroque art"), ("Q3083331", "Andean Baroque"), ("Q3635090", "Milanese Baroque"), ("Q954879", "Churrigueresque"),
   ("Q5327255", "Earthquake Baroque"), ("Q1811245", "barocco leccese"), ("Q8242964", "Hispanic baroque"), ("Q326469", "Portuguese baroque"),
   ("Q2359372", "Elizabethan Baroque"), ("Q5501689", "French Baroque architecture"), ("Q4408702", "Belarusian Baroque"), ("Q4176287", "baroque gothic"))
_h("baroque", True, ("Q911397", "baroque revival"), ("Q5346070", "Edwardian architecture"), ("Q84418145", "Rococo Revival architecture"))
_h("neoclassical", False, ("Q54111", "Neoclassical architecture"), ("Q170292", "Classicism"), ("Q14378", "Neoclassicism"), ("Q1400086", "Federal architecture"),
   ("Q1125300", "Georgian architecture"), ("Q191105", "Empire style"), ("Q264649", "Palladian architecture"), ("Q3621606", "Neoclassical architecture in Russia"),
   ("Q4198718", "classical architecture"), ("Q6092863", "Italian Neoclassical architecture"), ("Q388587", "Louis XVI style"), ("Q1788409", "Nordic Classicism"),
   ("Q3874654", "neoclassicism in Milan"), ("Q154432", "Biedermeier"), ("Q3931689", "Regency architecture"), ("Q1556741", "Gustavian style"),
   ("Q112711827", "Russian Empire style"), ("Q2740095", "Um 1800"))
_h("neoclassical", True, ("Q1513688", "Greek Revival architecture"), ("Q20897878", "Georgian Revival architecture"), ("Q20192147", "Neoclassicalism"),
   ("Q1134824", "Stalinist architecture"), ("Q4439247", "Stalinist Empire style"), ("Q11686646", "Socialist architecture in Poland"),
   ("Q50084199", "New Classical architecture"), ("Q93899018", "Soviet classicism"), ("Q4393722", "Retrospectivist architecture"),
   ("Q7382246", "Russian Neoclassical Revival"), ("Q23091252", "Stripped Classicism"), ("Q180902", "socialist realism"), ("Q384177", "Egyptian Revival architecture"),
   ("Q1289482", "Traditionalist School"), ("Q2748747", "Delftse School"), ("Q2130795", "Bossche School"), ("Q21652111", "monumentalism in architecture"),
   ("Q287025", "Nazi architecture"))
_h("historicist", False, ("Q2479493", "eclectic architecture"), ("Q51879601", "historicist architecture"), ("Q1268134", "Beaux-Arts"),
   ("Q565165", "Victorian architecture"), ("Q7270218", "Queen Anne style architecture in the United States"), ("Q529819", "Queen Anne style"),
   ("Q27958342", "Second Empire architecture in the United States and Canada"), ("Q174419", "Second Empire style"), ("Q277466", "historicism"),
   ("Q7616244", "Stick style"), ("Q1595728", "Heimatstil"), ("Q2256729", "Swiss chalet style"), ("Q189458", "academic art"), ("Q192068", "eclecticism"),
   ("Q2537632", "eclecticism in art"), ("Q55164904", "Queen Anne Revival architecture"), ("Q23752285", "Eclectic architecture in Russia"),
   ("Q12049741", "Romantic architecture"), ("Q5330714", "Eastlake Movement"), ("Q27958345", "Second Empire architecture in Europe"),
   ("Q1216982", "revivalism"), ("Q460501", "historicism"), ("Q1621045", "historicizing"), ("Q116245538", "industrial eclecticism"),
   ("Q105363923", "Haussmannian architecture"), ("Q466887", "Belle Époque"), ("Q133514349", "Spanish Eclectic architecture"),
   ("Q54979933", "Victorian Free Classical"), ("Q137216891", "Late Victorian Plain"), ("Q11417855", "Japanese-Western Eclectic Architecture"),
   ("Q1580216", "Noucentisme"), ("Q4221815", "brick style"), ("Q933661", "Novecento Italiano"), ("Q567789", "Federation architecture"))
_h("colonial", False, ("Q508475", "colonial architecture"), ("Q570074", "American colonial architecture"), ("Q5453505", "First Period"),
   ("Q5501716", "French Colonial"), ("Q12069738", "Spanish Colonial architecture"), ("Q5034667", "Cape Cod"), ("Q5184212", "Creole architecture in the United States"),
   ("Q7232704", "Portuguese colonial architecture"), ("Q112702185", "Dutch colonial architecture"))
_h("colonial", True, ("Q5148367", "Colonial Revival architecture"), ("Q3645460", "Spanish Colonial Revival architecture"), ("Q2700522", "Mission Revival architecture"),
   ("Q7937337", "Mediterranean Revival architecture"), ("Q7258468", "Pueblo Revival Style architecture"), ("Q5317260", "Dutch Colonial Revival architecture"),
   ("Q6905299", "Monterey Colonial architecture"))
_h("crafts", False, ("Q463382", "American Craftsman"), ("Q616358", "Prairie School architecture"), ("Q6974748", "National Park Service rustic"),
   ("Q2657199", "rustic architecture"), ("Q330369", "Arts and Crafts movement"), ("Q5673292", "Shingle style architecture"), ("Q4743854", "American Foursquare"),
   ("Q1077702", "national Romantic style"), ("Q36118", "organic architecture"), ("Q655556", "Heimatschutz architecture"), ("Q2136756", "Reform Architecture"),
   ("Q117005626", "Northern modern"), ("Q15613803", "Usonian architecture"), ("Q7954160", "WPA Rustic"), ("Q25393587", "Regionalism"),
   ("Q5705264", "regionalist architecture in Spain"))
_h("nouveau", False, ("Q1295040", "Art Nouveau architecture"), ("Q1122677", "Catalan modernism"), ("Q11686645", "Art Nouveau architecture in Italy"),
   ("Q47015062", "Valencian Art Nouveau"), ("Q61777202", "Geometric Art Nouveau"), ("Q1294605", "Jugendstil"), ("Q208208", "Vienna Secession"),
   ("Q660311", "Art nouveau in Milan"), ("Q20645040", "Stile Liberty"), ("Q11355242", "Brussels style"), ("Q112687131", "Bienne modernism"),
   ("Q1295289", "secessionist architecture in Hungary"), ("Q878985", "modernism (decorative art)"))
_h("deco", False, ("Q173782", "Art Deco"), ("Q12720942", "Art Deco architecture"), ("Q48976503", "Moderne architecture"), ("Q928960", "Streamline Moderne"),
   ("Q61459826", "Streamline Moderne architecture"), ("Q17182373", "PWA Moderne"), ("Q54912692", "Art Deco in the Land of Valencia"), ("Q9322693", "Rondocubism"))
_h("modern", False, ("Q245188", "modern architecture"), ("Q47942", "functionalism"), ("Q2535546", "rationalism"), ("Q162324", "International Style"),
   ("Q841977", "constructivist architecture"), ("Q1072060", "Chicago School"), ("Q11784483", "Neues Bauen"), ("Q24935410", "Soviet Modernist architecture"),
   ("Q1148060", "expressionist architecture"), ("Q478742", "Amsterdam School"), ("Q207103", "Constructivism"), ("Q574561", "New Objectivity"),
   ("Q1967635", "Postconstructivism"), ("Q42934", "cubism"), ("Q6840667", "mid-century modern"), ("Q1962399", "Nachkriegsmoderne"), ("Q124354", "Bauhaus"),
   ("Q478774", "purism"), ("Q115688756", "Rationalism of Lake Como"), ("Q468050", "Brick Expressionism"), ("Q6827366", "Miami Modern architecture"),
   ("Q333353", "futurist architecture"), ("Q1667680", "structuralism"), ("Q3271544", "neomodern"), ("Q600320", "architecture of the Fascist period"),
   ("Q65116247", "interwar period architecture"), ("Q108107298", "postwar modernism"), ("Q17104714", "Nieuwe Zakelijkheid"), ("Q2314870", "New Hague School"),
   ("Q60094901", "Rationalist architecture in the Land of Valencia"), ("Q207445", "De Stijl"), ("Q80113", "Expressionism"), ("Q11784484", "Modernist architecture in Poland"),
   ("Q717220", "Googie"), ("Q18746504", "New Formalism"), ("Q16931750", "Northwest Regional style"), ("Q108107402", "Bauhaus modernism"),
   ("Q12406815", "International style in Israel"), ("Q6095546", "First national architectural movement"))
_h("brutalist", False, ("Q994776", "brutalist architecture"), ("Q115096450", "(unlabelled subclass of brutalist architecture)"))
_h("postmodern", False, ("Q595448", "postmodern architecture"), ("Q186018", "contemporary architecture"), ("Q845318", "high-tech architecture"),
   ("Q238255", "deconstructivism"), ("Q17012219", "neo-futurism"), ("Q47783", "Postmodernism"), ("Q173436", "Minimalism"))
_h("islamic", False, ("Q212940", "Islamic architecture"), ("Q247492", "Moorish architecture"), ("Q16210807", "Mamluk architecture"),
   ("Q2860353", "Mudéjar architecture"), ("Q15011985", "Mudéjar style"), ("Q12052700", "Abbasid architecture"), ("Q2864672", "Art of Al-Andalus"),
   ("Q764675", "Mudéjar architecture of Aragon"), ("Q2864591", "art of Almoravides and Almohades"), ("Q16836366", "Fatimid architecture"),
   ("Q2147720", "Umayyad architecture"), ("Q127632740", "Anatolian Seljuk architecture"), ("Q2864629", "art of the Umayyads of Cordoba"),
   ("Q35583408", "Najdi architecture"), ("Q17998308", "(unlabelled: Javanese mosque style)"))
_h("islamic", True, ("Q74156", "Moorish Revival architecture"), ("Q614624", "neo-Mudéjar"))
_h("persian", False, ("Q5718239", "Qajar architecture"), ("Q5957125", "Safavid architecture"), ("Q17993891", "Pahlavi architecture"),
   ("Q7448523", "Seljuk architecture"), ("Q98399895", "Ilkhanid architecture"), ("Q16047695", "Timurid architecture"), ("Q5679012", "Zand architecture"),
   ("Q98406757", "Buyid architecture"), ("Q98399175", "Afsharid architecture"), ("Q111390205", "Nizari architecture"), ("Q98400041", "Ghaznavid architecture"),
   ("Q98400141", "Khwarazmian architecture"), ("Q98417627", "Ziyarid architecture"), ("Q98406896", "Samanid architecture"))
_h("ottoman", False, ("Q527449", "Ottoman architecture"))
_h("mughal", False, ("Q542261", "Mughal architecture"), ("Q825394", "Indo-Islamic architecture"))
_h("mughal", True, ("Q3374557", "Indo-Saracenic architecture"))
_h("hindu", False, ("Q24945352", "At-chala"), ("Q171309", "Dravidian architecture"), ("Q25204255", "Pancharatna"), ("Q3024819", "Deul"),
   ("Q6982098", "Navaratna"), ("Q24945384", "Ek-ratna"), ("Q80706", "Hindu temple architecture"), ("Q24905948", "Char-chala"), ("Q6276222", "Jor-bangla"),
   ("Q13640694", "Kalinga architecture"))
_h("chinese", False, ("Q957904", "Chinese architecture"))
_h("japanese", False, ("Q11268718", "zenpō-kōen-fun"), ("Q210684", "nagare-zukuri"), ("Q930545", "Shinmei-zukuri"), ("Q11394747", "circular kofun"),
   ("Q3193781", "Kasuga-zukuri"), ("Q11504353", "square kofun"), ("Q3155268", "Ishi-no-ma-zukuri"), ("Q11397225", "Zenpō-kōhō-fun"),
   ("Q11480883", "scallop-shaped kofun"), ("Q518007", "Giyōfū architecture"), ("Q1353902", "sukiya-zukuri"), ("Q11638385", "modern Japanese-style architecture"),
   ("Q3575224", "さやと"), ("Q3566879", "Wayō"), ("Q387874", "Taisha-zukuri"), ("Q106463430", "dozō"), ("Q94062224", "kakezukuri"), ("Q3125455", "Hachiman-zukuri"),
   ("Q11391751", "octagonal kofun"), ("Q8139947", "gasshō-zukuri"), ("Q11060089", "Imperial Crown Style"), ("Q935445", "minka"), ("Q3503635", "Sumiyoshi-zukuri"),
   ("Q11358496", "round-topped burial mound"))
_h("seasian", False, ("Q12472525", "Balinese architecture"), ("Q136557920", "Thai architecture"))
_h("other", False, ("Q130394325", "premodern architecture"), ("Q3621572", "Sikh architecture"))
_h("historicist", False, ("Q466675", "American Renaissance"))
_h("precolumbian", True, ("Q3933952", "Mayan Revival architecture"))

# Keyword rules for styles without a hand decision (checked in order; first match wins). (regex, family, revival)
KEYWORDS = [
    (r"\bbrutalis", "brutalist", False),
    (r"art deco|\bdeco\b|moderne\b", "deco", False),
    (r"art nouveau|jugendstil|secession|liberty|modernisme|nancy", "nouveau", False),
    (r"postmodern|deconstruct|high-tech|contemporary|blobitecture|neo-futur|minimal|parametric", "postmodern", False),
    (r"gothic revival|neo-?gothic|pseudo-gothic|gothic survival|castellated", "gothic", True),
    (r"romanesque revival|neo-?romanesque|neo-norman|rundbogen", "romanesque", True),
    (r"renaissance revival|neo-?renaissance|italianate", "renaissance", True),
    (r"baroque revival|neo-?baroque|rococo revival", "baroque", True),
    (r"greek revival|neo-?classic|neo-grec|neo-pompeian|classical revival|georgian revival", "neoclassical", True),
    (r"moorish revival|neo-?moorish|neo-?mud[eé]jar|neo-mamluk|moresque|moresco", "islamic", True),
    (r"byzantine revival|neo-?byzantine|russian revival", "byzantine", True),
    (r"colonial revival|mission revival|pueblo revival|spanish revival|territorial revival|monterey revival|peruvian revival", "colonial", True),
    (r"mayan revival|assyrian revival", "precolumbian", True),
    (r"neo-functional|neo-expression|neo-rational|neomodern|neo-constructiv", "modern", False),
    (r"neo-louis", "baroque", True),
    (r"revival|^neo-|^neo ", "historicist", True),
    (r"kofun|zukuri|japanese|minka|machiya|daibutsu|setch[uū]y[oō]|wa?y[oō]|shoin|shinden|buke|teishin|ryukyu", "japanese", False),
    (r"chinese|siheyuan|sanheyuan|hui-style|sichuan|paifang|pagoda|korean|hanok|xiangfang", "chinese", False),
    (r"khmer|thai|ayutthaya|burmese|javanese|balinese|malay|indonesia|vietnam|lao", "seasian", False),
    (r"maya\b|mayan|inca|aztec|mesoamerican|pre-columbian|olmec|zapotec|puuc|pueblo architecture", "precolumbian", False),
    (r"mughal|indo-islamic|indo-saracenic|tughlaq|qutb shahi|deccan|bengal sultanate", "mughal", False),
    (r"-chala|-ratna|dravidian|nagara|kalinga|hoysala|vesara|hindu|kakatiya|tamil|kerala|m[aā]ru-gurjara|deul|sikh", "hindu", False),
    (r"ottoman", "ottoman", False),
    (r"seljuk|ilkhanid|timurid|safavid|qajar|zand|pahlavi|afsharid|buyid|ghaznavid|samanid|saffarid|ziyarid|isfahani|razi style|azari|khwarazm|iran", "persian", False),
    (r"islamic|mosque|moorish|mud[eé]jar|mamluk|umayyad|abbasid|fatimid|almohad|almoravid|nasrid|marinid|ayyubid|rashidun|al-andalus|andalus|arab|berber|maghreb|moroccan|najdi|swahili|damascene|mozarab", "islamic", False),
    (r"achaemenid|sasanian|parthian|seleucid|elamite|median|hellenistic|ancient|roman architecture|greek architecture|etruscan|egyptian|cyclopean|polygonal masonry|classical antiquity|doric|ionic|corinthian|tuscan order|composite order|tetrapylon|peripteral|tetrastyle|second style", "ancient", False),
    (r"byzantine|armenian|georgia|orthodox|kievan|pskov|novgorod|vladimir|moscow school|uzorochye|serbo|morava|rascian|coptic|early christian|caucasian albanian", "byzantine", False),
    (r"pre-romanesque|romanesque|norman|carolingian|ottonian|visigothic|asturian|anglo-saxon|lombard architecture|mosan art|repoblaci", "romanesque", False),
    (r"gothic|manueline|isabelline|perpendicular|rayonnant|flamboyant|decorated|early english|tudor architecture|chiaramonte", "gothic", False),
    (r"renaissance|louis xii style|villa veneta|mannerism|mannerist|plateresque|herrerian|jacobean|elizabethan|wrenaissance|chão|soft portuguese|weser", "renaissance", False),
    (r"baroque|barocco|barroco|rococo|churriguer|louis xiv|louis xv|louis xiii|r[ée]gence|grand si[eè]cle|carolean|barocchetto|joanine", "baroque", False),
    (r"neocl[aá]s|classicism|classicist|palladian|georgian|federal|empire style|adam style|directoire|louis xvi|regency|biedermeier|gustavian|zopf|pombaline|jeffersonian|waterstaat|stalinist|socialist realism|antebellum|grand manner", "neoclassical", False),
    (r"colonial|cape dutch|creole|tidewater|indies|bahay|cape cod|saltbox", "colonial", False),
    (r"arts and crafts|craftsman|prairie|rustic|bungalow|foursquare|usonia|organic|national romantic|dragestil|heimatschutz|adirondack|storybook|shingle style|anthroposophic|minimal traditional", "crafts", False),
    (r"brutal|metabolism|modern|functionalis|rationalis|international style|constructivis|bauhaus|expressionis|de stijl|new objectivity|zakelijkheid|futuris|structuralism|purism|googie|formalism|neues bauen|amsterdam school|chicago school|panel system|fascist|littorio|tropical|expo style|glass architecture|sarasota|neoconstructivism|sculpturalism|machinism", "modern", False),
    (r"eclectic|historicis|historism|victorian|beaux-arts|second empire|queen anne|stick style|eastlake|ch[aâ]teauesque|swiss chalet|heimatstil|gr[uü]nderzeit|wilhelminian|belle [ée]poque|haussmann|umbertino|archduke|hollywood regency|city beautiful|troubadour|romantic", "historicist", False),
    (r"vernacular|folk|wooden|timber|half-timber|log |cottage|farmhouse|house\b|steinbloss|dogtrot|shotgun|pen architecture|long house|masia|chalet|stave", "vernacular", False),
]


def keyword_family(label):
    s = (label or "").lower()
    if not s:
        return None
    for rx, fam, rev in KEYWORDS:
        if re.search(rx, s):
            return fam, rev
    return None
