from telethon import events
from telethon.tl.custom import Button
import re
from .utils import format_number

# Dictionary to convert Persian digits to English digits
PERSIAN_DIGITS = {
    '۰': '0',
    '۱': '1',
    '۲': '2',
    '۳': '3',
    '۴': '4',
    '۵': '5',
    '۶': '6',
    '۷': '7',
    '۸': '8',
    '۹': '9',
}

# Keywords that trigger this handler
TRIGGERS = ['تبدیل', 'convert', 'تبدیل_ارز', 'currency_convert']

# Regular expression pattern to match conversion requests
# Format: amount currency to currency
# Examples: 100 usd to toman, 1000 toman to eur
CONVERSION_PATTERN = re.compile(r'(\d+(?:\.\d+)?)\s*([a-zA-Z\u0600-\u06FF]+)\s*(?:به|to)\s*([a-zA-Z\u0600-\u06FF]+)', re.IGNORECASE)

# Simple pattern to match just amount and currency
# Examples: 100 usd, 1000 toman, ۱۰۰ دلار
SIMPLE_AMOUNT_PATTERN = re.compile(r'(\d+(?:\.\d+)?)\s*([a-zA-Z\u0600-\u06FF]+)', re.IGNORECASE)

# Pattern to identify messages consisting only of numbers, dots, commas, and spaces (English or Persian)
ONLY_NUMBERS_PATTERN = re.compile(r"^[\d۰-۹\s\.,]+$")

# Currency code mappings (English, Persian, and common abbreviations)
CURRENCY_CODES = {
    # Main currencies
    'دلار': 'USD', 'dollar': 'USD', 'usd': 'USD', 'دلار آمریکا': 'USD',
    'یورو': 'EUR', 'euro': 'EUR', 'eur': 'EUR', 'یورو اروپا': 'EUR',
    'پوند': 'GBP', 'pound': 'GBP', 'gbp': 'GBP', 'پوند انگلیس': 'GBP',
    'درهم': 'AED', 'dirham': 'AED', 'aed': 'AED', 'درهم امارات': 'AED',
    'لیر': 'TRY', 'lira': 'TRY', 'try': 'TRY', 'لیر ترکیه': 'TRY',
    'تومان': 'TOMAN', 'toman': 'TOMAN', 'تومن': 'TOMAN', 'irt': 'TOMAN',
    'ریال': 'IRR', 'rial': 'IRR', 'irr': 'IRR',
    
    # Additional currencies - Part 1
    'دلار کانادا': 'CAD', 'cad': 'CAD', 'canadian dollar': 'CAD',
    'دلار استرالیا': 'AUD', 'aud': 'AUD', 'australian dollar': 'AUD',
    'یوان': 'CNY', 'yuan': 'CNY', 'cny': 'CNY', 'یوان چین': 'CNY',
    'ین ژاپن': 'JPY', 'yen': 'JPY', 'jpy': 'JPY', 'ین ژاپن (100 ین)': 'JPY',
    'فرانک سوئیس': 'CHF', 'swiss franc': 'CHF', 'chf': 'CHF',
    'رینگیت': 'MYR', 'ringgit': 'MYR', 'myr': 'MYR', 'رینگیت مالزی': 'MYR',
    'بات': 'THB', 'baht': 'THB', 'thb': 'THB', 'بات تایلند': 'THB',
    'دلار سنگاپور': 'SGD', 'sgd': 'SGD', 'singapore dollar': 'SGD',
    'دلار هنگ کنگ': 'HKD', 'hkd': 'HKD', 'hong kong dollar': 'HKD',
    'روپیه': 'INR', 'rupee': 'INR', 'inr': 'INR', 'روپیه هند': 'INR',
    'وون': 'KRW', 'won': 'KRW', 'krw': 'KRW', 'وون کره جنوبی': 'KRW',
    'کرون': 'SEK', 'krona': 'SEK', 'sek': 'SEK', 'کرون سوئد': 'SEK',
    'کرون نروژ': 'NOK', 'nok': 'NOK', 'norwegian krone': 'NOK',
    'کرون دانمارک': 'DKK', 'dkk': 'DKK', 'danish krone': 'DKK',
    'روبل': 'RUB', 'ruble': 'RUB', 'rub': 'RUB', 'روبل روسیه': 'RUB',
    'منات': 'AZN', 'manat': 'AZN', 'azn': 'AZN', 'منات آذربایجان': 'AZN',
    'درام': 'AMD', 'dram': 'AMD', 'amd': 'AMD', 'درام ارمنستان': 'AMD',
    'لاری': 'GEL', 'lari': 'GEL', 'gel': 'GEL', 'لاری گرجستان': 'GEL',
    'سوم': 'KGS', 'som': 'KGS', 'kgs': 'KGS', 'سوم قرقیزستان': 'KGS',
    'سامانی': 'TJS', 'somoni': 'TJS', 'tjs': 'TJS', 'سامانی تاجیکستان': 'TJS',
    'سوم ازبکستان': 'UZS', 'uzs': 'UZS', 'uzbekistan som': 'UZS',
    'تنگه': 'KZT', 'tenge': 'KZT', 'kzt': 'KZT', 'تنگه قزاقستان': 'KZT',
    'افغانی': 'AFN', 'afghani': 'AFN', 'afn': 'AFN', 'افغانی افغانستان': 'AFN',
    'روپیه پاکستان': 'PKR', 'pkr': 'PKR', 'pakistani rupee': 'PKR',
    'پوند سوریه': 'SYP', 'syp': 'SYP', 'syrian pound': 'SYP', 'لیره سوریه': 'SYP',
    'دینار عراق': 'IQD', 'iqd': 'IQD', 'iraqi dinar': 'IQD',
    'ریال عربستان': 'SAR', 'sar': 'SAR', 'saudi riyal': 'SAR',
    'ریال قطر': 'QAR', 'qar': 'QAR', 'qatari riyal': 'QAR',
    'دینار کویت': 'KWD', 'kwd': 'KWD', 'kuwaiti dinar': 'KWD',
    'دینار بحرین': 'BHD', 'bhd': 'BHD', 'bahraini dinar': 'BHD',
    'ریال عمان': 'OMR', 'omr': 'OMR', 'omani rial': 'OMR',
    'ریال یمن': 'YER', 'yer': 'YER', 'yemeni rial': 'YER',
    'انس طلا': 'XAU', 'gold': 'XAU', 'طلا': 'XAU', 'اونس طلا': 'XAU',
    'انس نقره': 'XAG', 'silver': 'XAG', 'نقره': 'XAG', 'اونس نقره': 'XAG',
    'انس پلاتین': 'XPT', 'platinum': 'XPT', 'پلاتین': 'XPT', 'اونس پلاتین': 'XPT',
    'انس پالادیوم': 'XPD', 'palladium': 'XPD', 'پالادیوم': 'XPD', 'اونس پالادیوم': 'XPD',
    
    # Cryptocurrencies
    'بیت کوین': 'BTC', 'bitcoin': 'BTC', 'btc': 'BTC',
    'اتریوم': 'ETH', 'ethereum': 'ETH', 'eth': 'ETH',
    'تتر': 'USDT', 'tether': 'USDT', 'usdt': 'USDT',
    'بایننس کوین': 'BNB', 'binance coin': 'BNB', 'bnb': 'BNB',
    'کاردانو': 'ADA', 'cardano': 'ADA', 'ada': 'ADA',
    'ریپل': 'XRP', 'ripple': 'XRP', 'xrp': 'XRP',
    'دوج کوین': 'DOGE', 'dogecoin': 'DOGE', 'doge': 'DOGE',
    'پولکادات': 'DOT', 'polkadot': 'DOT', 'dot': 'DOT',
    'سولانا': 'SOL', 'solana': 'SOL', 'sol': 'SOL',
    'شیبا اینو': 'SHIB', 'shiba inu': 'SHIB', 'shib': 'SHIB',
    'لایت کوین': 'LTC', 'litecoin': 'LTC', 'ltc': 'LTC',
    'ترون': 'TRX', 'tron': 'TRX', 'trx': 'TRX',
    'آوالانچ': 'AVAX', 'avalanche': 'AVAX', 'avax': 'AVAX',
    'چین لینک': 'LINK', 'chainlink': 'LINK', 'link': 'LINK',
    'یونی سواپ': 'UNI', 'uniswap': 'UNI', 'uni': 'UNI',
    'کازماس': 'ATOM', 'cosmos': 'ATOM', 'atom': 'ATOM',
    'مونرو': 'XMR', 'monero': 'XMR', 'xmr': 'XMR',
    'اتریوم کلاسیک': 'ETC', 'ethereum classic': 'ETC', 'etc': 'ETC',
    'فایل کوین': 'FIL', 'filecoin': 'FIL', 'fil': 'FIL',
    
    # Additional currencies - Part 2
    'بیر اتیوپی': 'ETB', 'etb': 'ETB', 'ethiopian birr': 'ETB',
    'فرانک گینه': 'GNF', 'gnf': 'GNF', 'guinean franc': 'GNF',
    'گواتزال گواتمالا': 'GTQ', 'gtq': 'GTQ', 'guatemalan quetzal': 'GTQ',
    'دلار گویان': 'GYD', 'gyd': 'GYD', 'guyanese dollar': 'GYD',
    'لمپیرا هندوراس': 'HNL', 'hnl': 'HNL', 'honduran lempira': 'HNL',
    'گورده هایتی': 'HTG', 'htg': 'HTG', 'haitian gourde': 'HTG', 'گورد هائیتی': 'HTG',
    'روپیه اندونزی': 'IDR', 'idr': 'IDR', 'indonesian rupiah': 'IDR',
    'شکل جدید اسرائیل': 'ILS', 'ils': 'ILS', 'israeli new shekel': 'ILS',
    'دینار اردن': 'JOD', 'jod': 'JOD', 'jordanian dinar': 'JOD',
    'شیلینگ کنیا': 'KES', 'kes': 'KES', 'kenyan shilling': 'KES',
    'کیپ لائوس': 'LAK', 'lak': 'LAK', 'lao kip': 'LAK', 'kip': 'LAK',
    'پوند لبنان': 'LBP', 'lbp': 'LBP', 'lebanese pound': 'LBP',
    'روپیه سریلانکا': 'LKR', 'lkr': 'LKR', 'sri lankan rupee': 'LKR',
    'دلار لیبریا': 'LRD', 'lrd': 'LRD', 'liberian dollar': 'LRD',
    'لوتی لسوتو': 'LSL', 'lsl': 'LSL', 'lesotho loti': 'LSL',
    'دینار لیبی': 'LYD', 'lyd': 'LYD', 'libyan dinar': 'LYD',
    'مراکش درهم': 'MAD', 'mad': 'MAD', 'moroccan dirham': 'MAD', 'دزد': 'MAD',
    'لئوی مولداوی': 'MDL', 'mdl': 'MDL', 'moldovan leu': 'MDL', 'leu': 'MDL', 'لئو مولداوی': 'MDL',
    'آریاری مالاگاسی': 'MGA', 'mga': 'MGA', 'malagasy ariary': 'MGA', 'آریاری ماداگاسکار': 'MGA',
    'دنار مقدونیه': 'MKD', 'mkd': 'MKD', 'macedonian denar': 'MKD', 'denar': 'MKD',
    'کیات میانمار': 'MMK', 'mmk': 'MMK', 'myanmar kyat': 'MMK', 'kyat': 'MMK',
    'توگروگ مغولستان': 'MNT', 'mnt': 'MNT', 'mongolian tugrik': 'MNT', 'tugrik': 'MNT',
    'پاتاکای ماکائو': 'MOP', 'mop': 'MOP', 'macanese pataca': 'MOP', 'pataca': 'MOP', 'پاتاکا ماکائو': 'MOP',
    'اوگوئیای موریتانی': 'MRU', 'mru': 'MRU', 'mauritanian ouguiya': 'MRU', 'ouguiya': 'MRU',
    'روپیه موریس': 'MUR', 'mur': 'MUR', 'mauritian rupee': 'MUR',
    'روفیا مالدیو': 'MVR', 'mvr': 'MVR', 'maldivian rufiyaa': 'MVR', 'rufiyaa': 'MVR',
    'کواچای مالاوی': 'MWK', 'mwk': 'MWK', 'malawian kwacha': 'MWK', 'kwacha': 'MWK', 'کواچا مالاوی': 'MWK',
    'پزوی مکزیک': 'MXN', 'mxn': 'MXN', 'mexican peso': 'MXN',
    'متیکال موزامبیک': 'MZN', 'mzn': 'MZN', 'mozambican metical': 'MZN', 'metical': 'MZN',
    'دلار نامیبیا': 'NAD', 'nad': 'NAD', 'namibian dollar': 'NAD', 'دلار نامبیا': 'NAD',
    'نیرا نیجریه': 'NGN', 'ngn': 'NGN', 'nigerian naira': 'NGN', 'naira': 'NGN', 'نایرای نیجریه': 'NGN',
    'کوردوبا نیکاراگوئه': 'NIO', 'nio': 'NIO', 'nicaraguan córdoba': 'NIO', 'کوردوبای نیکاراگوئه': 'NIO',
    'روپیه نپال': 'NPR', 'npr': 'NPR', 'nepalese rupee': 'NPR',
    'دلار نیوزیلند': 'NZD', 'nzd': 'NZD', 'new zealand dollar': 'NZD',
    'بولبوئا پاناما': 'PAB', 'pab': 'PAB', 'panamanian balboa': 'PAB', 'balboa': 'PAB', 'بالبوآ پاناما': 'PAB',
    'نوئووسول پرو': 'PEN', 'pen': 'PEN', 'peruvian nuevo sol': 'PEN', 'nuevo sol': 'PEN',
    'کینا پاپوا گینه نو': 'PGK', 'pgk': 'PGK', 'papua new guinean kina': 'PGK', 'kina': 'PGK', 'کینای پاپوآ گینه نو': 'PGK',
    'پزوی فیلیپین': 'PHP', 'php': 'PHP', 'philippine peso': 'PHP',
    'زلوتی لهستان': 'PLN', 'pln': 'PLN', 'polish złoty': 'PLN', 'złoty': 'PLN',
    'گورانی پاراگوئه': 'PYG', 'pyg': 'PYG', 'paraguayan guaraní': 'PYG', 'guaraní': 'PYG', 'گوارانی پاراگوئه': 'PYG',
    'لئو رومانی': 'RON', 'ron': 'RON', 'romanian leu': 'RON', 'لئوی رومانی': 'RON',
    'دینار صربستان': 'RSD', 'rsd': 'RSD', 'serbian dinar': 'RSD',
    'فرانک رواندا': 'RWF', 'rwf': 'RWF', 'rwandan franc': 'RWF',
    'دلار جزایر سلیمان': 'SBD', 'sbd': 'SBD', 'solomon islands dollar': 'SBD',
    'روپیه سیشل': 'SCR', 'scr': 'SCR', 'seychellois rupee': 'SCR',
    'پوند سودان': 'SDG', 'sdg': 'SDG', 'sudanese pound': 'SDG',
    'لئون سیرالئون': 'SLE', 'sle': 'SLE', 'sierra leonean leone': 'SLE', 'leone': 'SLE',
    'شیلینگ سومالی': 'SOS', 'sos': 'SOS', 'somali shilling': 'SOS', 'shilling': 'SOS',
    'دلار سورینام': 'SRD', 'srd': 'SRD', 'surinamese dollar': 'SRD',
    'پوند جنوب سودان': 'SSP', 'ssp': 'SSP', 'south sudanese pound': 'SSP',
    'دبرای سائوتومه و پرینسیپ': 'STN', 'stn': 'STN', 'são tomé and príncipe dobra': 'STN', 'dobra': 'STN',
    'کولون السالوادور': 'SVC', 'svc': 'SVC', 'salvadoran colón': 'SVC', 'colón': 'SVC', 'کولون سالوادور': 'SVC',
    'لیلانگی سوازیلند': 'SZL', 'szl': 'SZL', 'swazi lilangeni': 'SZL', 'lilangeni': 'SZL', 'لیلانگنی سوازیلند': 'SZL',
    'دلار جدید تایوان': 'TWD', 'twd': 'TWD', 'new taiwan dollar': 'TWD',
    'شیلینگ تانزانیا': 'TZS', 'tzs': 'TZS', 'tanzanian shilling': 'TZS',
    'هریونای اوکراین': 'UAH', 'uah': 'UAH', 'ukrainian hryvnia': 'UAH', 'hryvnia': 'UAH',
    'شیلینگ اوگاندا': 'UGX', 'ugx': 'UGX', 'ugandan shilling': 'UGX',
    'پزوی اروگوئه': 'UYU', 'uyu': 'UYU', 'uruguayan peso': 'UYU', 'پزوی اوروگوئه': 'UYU',
    'بولیوار ونزوئلا': 'VES', 'ves': 'VES', 'venezuelan bolívar soberano': 'VES', 'bolívar soberano': 'VES',
    'دونگ ویتنام': 'VND', 'vnd': 'VND', 'vietnamese đồng': 'VND', 'đồng': 'VND', 'دانگ ویتنام': 'VND',
    'واتوی وانوآتو': 'VUV', 'vuv': 'VUV', 'vanuatu vatu': 'VUV', 'vatu': 'VUV',
    'تالای ساموآ': 'WST', 'wst': 'WST', 'samoan tālā': 'WST', 'tālā': 'WST',
    'فرانک آفریقای مرکزی': 'XAF', 'xaf': 'XAF', 'central african cfa franc': 'XAF',
    'دلار شرق کارائیب': 'XCD', 'xcd': 'XCD', 'east caribbean dollar': 'XCD',
    'فرانک آفریقای غربی': 'XOF', 'xof': 'XOF', 'west african cfa franc': 'XOF',
    'فرانک اقیانوسیه': 'XPF', 'xpf': 'XPF', 'cfp franc': 'XPF', 'franc pacifique': 'XPF',
    'کواچا زامبیا': 'ZMW', 'zmw': 'ZMW', 'zambian kwacha': 'ZMW', 'کواچای زامبیا': 'ZMW',
    'دلار زیمبابوه': 'ZWL', 'zwl': 'ZWL', 'zimbabwean dollar': 'ZWL',
    'منات ترکمنستان': 'TMT', 'tmt': 'TMT', 'turkmenistan manat': 'TMT', 'tmm': 'TMT',
    'لک آلبانی': 'ALL', 'all': 'ALL', 'albanian lek': 'ALL', 'lek': 'ALL',
    'دلار باربادوس': 'BBD', 'bbd': 'BBD', 'barbadian dollar': 'BBD',
    'تاکا بنگلادش': 'BDT', 'bdt': 'BDT', 'bangladeshi taka': 'BDT', 'taka': 'BDT',
    'لو بلغارستان': 'BGN', 'bgn': 'BGN', 'bulgarian lev': 'BGN', 'lev': 'BGN',
    'فرانک بوروندی': 'BIF', 'bif': 'BIF', 'burundian franc': 'BIF',
    'دلار برونئی': 'BND', 'bnd': 'BND', 'brunei dollar': 'BND',
    'دلار باهاماس': 'BSD', 'bsd': 'BSD', 'bahamian dollar': 'BSD',
    'پوله بوتسوانا': 'BWP', 'bwp': 'BWP', 'botswana pula': 'BWP', 'pula': 'BWP',
    'روبل بلاروس': 'BYN', 'byn': 'BYN', 'belarusian ruble': 'BYN',
    'دلار بلیز': 'BZD', 'bzd': 'BZD', 'belize dollar': 'BZD',
    'پزوی کوبا': 'CUP', 'cup': 'CUP', 'cuban peso': 'CUP',
    'کرون چک': 'CZK', 'czk': 'CZK', 'czech koruna': 'CZK', 'koruna': 'CZK',
    'فرانک جیبوتی': 'DJF', 'djf': 'DJF', 'djiboutian franc': 'DJF',
    'پزوی دومنیکن': 'DOP', 'dop': 'DOP', 'dominican peso': 'DOP',
    'دینار الجزایر': 'DZD', 'dzd': 'DZD', 'algerian dinar': 'DZD',
    'کونا کرواسی': 'HRK', 'hrk': 'HRK', 'croatian kuna': 'HRK', 'kuna': 'HRK',
    'کرونا ایسلند': 'ISK', 'isk': 'ISK', 'icelandic króna': 'ISK', 'króna': 'ISK',
    'دلار جامایکا': 'JMD', 'jmd': 'JMD', 'jamaican dollar': 'JMD',
    'ریل کامبوج': 'KHR', 'khr': 'KHR', 'cambodian riel': 'KHR', 'riel': 'KHR',
    'فرانک کومور': 'KMF', 'kmf': 'KMF', 'comorian franc': 'KMF',
    'پوند سینت هلنا': 'SHP', 'shp': 'SHP', 'saint helena pound': 'SHP',
    'دینار تونس': 'TND', 'tnd': 'TND', 'tunisian dinar': 'TND',
    'دلار ترینیداد و توباگو': 'TTD', 'ttd': 'TTD', 'trinidad and tobago dollar': 'TTD',
    'سدی غنا': 'GHS', 'ghs': 'GHS', 'ghanaian cedi': 'GHS', 'cedi': 'GHS',
    'سول پرو': 'PEN', 'pen': 'PEN', 'peruvian sol': 'PEN', 'sol': 'PEN',
    'پزوی شیلی': 'CLP', 'clp': 'CLP', 'chilean peso': 'CLP',
    'پوند مصر': 'EGP', 'egp': 'EGP', 'egyptian pound': 'EGP',
    'رئال برزیل': 'BRL', 'brl': 'BRL', 'brazilian real': 'BRL', 'real': 'BRL',
    'پزوی کلمبیا': 'COP', 'cop': 'COP', 'colombian peso': 'COP',
    'پزوی آرژانتین': 'ARS', 'ars': 'ARS', 'argentine peso': 'ARS',
    'دلار جزایر کیمن': 'KYD', 'kyd': 'KYD', 'cayman islands dollar': 'KYD',
    'فورینت مجارستان': 'HUF', 'huf': 'HUF', 'hungarian forint': 'HUF', 'forint': 'HUF',
    'هریونیا اوکراین': 'UAH', 'uah': 'UAH', 'ukrainian hryvnia': 'UAH',
    'رند آفریقای جنوبی': 'ZAR', 'zar': 'ZAR', 'south african rand': 'ZAR', 'rand': 'ZAR',
    'دلار فیجی': 'FJD', 'fjd': 'FJD', 'fijian dollar': 'FJD',
    'فرانک آفریقای غربی': 'XOF', 'xof': 'XOF', 'west african cfa franc': 'XOF',
    'دلاسی گامبیا': 'GMD', 'gmd': 'GMD', 'gambian dalasi': 'GMD', 'dalasi': 'GMD',
    'فرانک آفریقا': 'XAF', 'xaf': 'XAF', 'central african cfa franc': 'XAF',
    'وانواتو واتو': 'VUV', 'vuv': 'VUV', 'vanuatu vatu': 'VUV',
    'آنتیل گیلدر هلند': 'ANG', 'ang': 'ANG', 'antillean guilder': 'ANG', 'guilder': 'ANG',
    'دوبرا سائوتومه و پرنسیپ': 'STN', 'stn': 'STN', 'são tomé and príncipe dobra': 'STN',
    'دلار کارائیب شرقی': 'XCD', 'xcd': 'XCD', 'east caribbean dollar': 'XCD'
}

async def handle_currency(event, client):
    """Handle currency conversion requests"""
    # Get the message text
    message_text = event.message.text.strip()

    # If the message consists only of numbers (and formatting chars), do nothing.
    if ONLY_NUMBERS_PATTERN.fullmatch(message_text):
        # Check if it might still contain a trigger word (e.g. "123 convert")
        # This is a safeguard. If it's purely numbers, the patterns below shouldn't match anyway.
        if not any(trigger.lower() in message_text.lower() for trigger in TRIGGERS):
             raise events.StopPropagation # MODIFIED: Stop other handlers

    # Direct check for Pakistani Rupee to ensure it's handled correctly
    if 'روپیه پاکستان' in message_text.lower() or 'پاکستان روپیه' in message_text.lower():
        # Extract the amount using regex
        amount_match = re.search(r'(\d[\d,\s\.]*|[۰-۹][۰-۹,\s\.]*)', message_text)
        if amount_match:
            try:
                amount_str = amount_match.group(1)
                # Convert Persian digits to English
                amount_str = ''.join([str(PERSIAN_DIGITS.get(c, c)) for c in amount_str])
                # Remove commas and spaces
                amount_str = amount_str.replace(',', '').replace(' ', '')
                amount = float(amount_str)
                
                # Get currency data
                data = event.client.currency_data
                if not data:
                    await event.respond('متاسفانه در حال حاضر امکان دریافت اطلاعات نرخ ارز وجود ندارد. ❌')
                    return
                
                # Use the fallback rate for Pakistani Rupee
                pkr_rate = 0.15  # This is the fallback rate we defined
                converted_amount = amount * pkr_rate
                
                # Format the response
                formatted_amount = format_number(amount)
                formatted_result = format_number(converted_amount)
                
                message = f"""💱 تبدیل ارز

{formatted_amount} روپیه پاکستان = {formatted_result} تومان

📊 نرخ تبدیل: 1 روپیه پاکستان = {format_number(pkr_rate)} تومان
⏱ آخرین بروزرسانی: نامشخص"""
                
                await event.respond(message)
                return
            except ValueError:
                pass
    
    # Try to parse conversion request
    match = CONVERSION_PATTERN.search(message_text)
    simple_match = None
    
    if not match:
        # Try to match simple pattern (just amount and currency)
        simple_match = SIMPLE_AMOUNT_PATTERN.search(message_text)
        if not simple_match:
            # If we're here because of a trigger word, show help
            if any(trigger in message_text.lower() for trigger in TRIGGERS):
                await show_conversion_help(event, client)
            # Otherwise, don't respond - it's not a currency conversion request
            return
    
    # Handle simple pattern (convert to Toman automatically)
    if simple_match:
        amount_str, from_currency = simple_match.groups()
        to_currency = 'تومان'  # Default target currency is Toman
    else:
        # Extract conversion parameters from full pattern
        amount_str, from_currency, to_currency = match.groups()
    
    try:
        amount = float(amount_str)
        
        # Add a limit to prevent extremely large numbers
        MAX_AMOUNT = 1000000000  # 1 billion
        if amount > MAX_AMOUNT:
            await event.respond(f'❌ مقدار وارد شده بسیار بزرگ است. لطفاً عددی کمتر از {format_number(MAX_AMOUNT)} وارد کنید.')
            return
    except ValueError:
        await event.respond('❌ مقدار وارد شده معتبر نیست. لطفاً یک عدد معتبر وارد کنید.')
        return
    
    # Normalize currency codes
    from_currency = from_currency.lower().strip()
    to_currency = to_currency.lower().strip()
    
    # Add specific phrases for exact matching
    EXACT_CURRENCY_PHRASES = {
        # Pakistani Rupee (highest priority to avoid confusion)
        'روپیه پاکستان': 'PKR',
        'پاکستان روپیه': 'PKR',
        'پاکستانی روپیه': 'PKR',
        'pakistani rupee': 'PKR',
        'pakistan rupee': 'PKR',
        'pkr': 'PKR',
        
        # Indian Rupee
        'روپیه هند': 'INR',
        'هند روپیه': 'INR',
        'هندی روپیه': 'INR',
        'indian rupee': 'INR',
        'india rupee': 'INR',
        'inr': 'INR',
        'دلار کانادا': 'CAD',
        'canadian dollar': 'CAD',
        'canada dollar': 'CAD',
        'دلار استرالیا': 'AUD',
        'australian dollar': 'AUD',
        'australia dollar': 'AUD',
        'دلار نیوزیلند': 'NZD',
        'new zealand dollar': 'NZD',
        'دلار سنگاپور': 'SGD',
        'singapore dollar': 'SGD',
        'دلار هنگ کنگ': 'HKD',
        'hong kong dollar': 'HKD',
        'دلار تایوان': 'TWD',
        'taiwan dollar': 'TWD',
        'ریال سعودی': 'SAR',
        'saudi riyal': 'SAR',
        'ریال قطر': 'QAR',
        'qatari riyal': 'QAR',
        'ریال عمان': 'OMR',
        'omani riyal': 'OMR',
        'ریال یمن': 'YER',
        'yemeni riyal': 'YER',
        'دینار کویت': 'KWD',
        'kuwaiti dinar': 'KWD',
        'دینار بحرین': 'BHD',
        'bahraini dinar': 'BHD',
        'دینار عراق': 'IQD',
        'iraqi dinar': 'IQD',
        'دینار اردن': 'JOD',
        'jordanian dinar': 'JOD',
        'دینار لیبی': 'LYD',
        'libyan dinar': 'LYD',
        'دینار الجزایر': 'DZD',
        'algerian dinar': 'DZD',
        'دینار تونس': 'TND',
        'tunisian dinar': 'TND',
        'درهم امارات': 'AED',
        'uae dirham': 'AED',
        'emirati dirham': 'AED',
        'درهم مراکش': 'MAD',
        'moroccan dirham': 'MAD',
        'پوند انگلیس': 'GBP',
        'پوند بریتانیا': 'GBP',
        'british pound': 'GBP',
        'pound sterling': 'GBP',
        'پوند مصر': 'EGP',
        'egyptian pound': 'EGP',
        'پوند سودان': 'SDG',
        'sudanese pound': 'SDG',
        'لیره لبنان': 'LBP',
        'lebanese pound': 'LBP',
        'لیره سوریه': 'SYP',
        'syrian pound': 'SYP',
        'لیر ترکیه': 'TRY',
        'turkish lira': 'TRY',
        'فرانک سوئیس': 'CHF',
        'swiss franc': 'CHF',
        'روبل روسیه': 'RUB',
        'russian ruble': 'RUB',
        'ین ژاپن': 'JPY',
        'japanese yen': 'JPY',
        'یوان چین': 'CNY',
        'chinese yuan': 'CNY',
        'وون کره جنوبی': 'KRW',
        'south korean won': 'KRW',
        'پزوی مکزیک': 'MXN',
        'mexican peso': 'MXN',
        'پزوی فیلیپین': 'PHP',
        'philippine peso': 'PHP',
        'پزوی آرژانتین': 'ARS',
        'argentine peso': 'ARS',
        'پزوی شیلی': 'CLP',
        'chilean peso': 'CLP',
        'پزوی کلمبیا': 'COP',
        'colombian peso': 'COP',
        'رئال برزیل': 'BRL',
        'brazilian real': 'BRL',
        'رند آفریقای جنوبی': 'ZAR',
        'south african rand': 'ZAR',
        'رینگیت مالزی': 'MYR',
        'malaysian ringgit': 'MYR',
        'بات تایلند': 'THB',
        'thai baht': 'THB',
        'دونگ ویتنام': 'VND',
        'vietnamese dong': 'VND',
        'افغانی': 'AFN',
        'afghani': 'AFN',
        'تاکا بنگلادش': 'BDT',
        'bangladeshi taka': 'BDT'
    }
    
    # First check for exact phrases - these take highest priority
    from_code = None
    to_code = None
    
    for phrase, code in EXACT_CURRENCY_PHRASES.items():
        if phrase in from_currency:
            from_code = code
            break
    
    for phrase, code in EXACT_CURRENCY_PHRASES.items():
        if phrase in to_currency:
            to_code = code
            break
    
    # If exact phrases weren't found, try the CURRENCY_CODES dictionary
    if from_code is None:
        from_code = CURRENCY_CODES.get(from_currency)
    
    if to_code is None:
        to_code = CURRENCY_CODES.get(to_currency)
    
    # Special handling for specific currencies that might be confused
    # Dollars
    if 'دلار' in from_currency or 'dollar' in from_currency:
        if 'کانادا' in from_currency or 'canada' in from_currency:
            from_code = 'CAD'
        elif 'استرالیا' in from_currency or 'australia' in from_currency:
            from_code = 'AUD'
        elif 'نیوزیلند' in from_currency or 'new zealand' in from_currency:
            from_code = 'NZD'
        elif 'سنگاپور' in from_currency or 'singapore' in from_currency:
            from_code = 'SGD'
        elif 'هنگ کنگ' in from_currency or 'hong kong' in from_currency:
            from_code = 'HKD'
        elif 'تایوان' in from_currency or 'taiwan' in from_currency:
            from_code = 'TWD'
        elif 'برونئی' in from_currency or 'brunei' in from_currency:
            from_code = 'BND'
        elif 'لیبریا' in from_currency or 'liberia' in from_currency:
            from_code = 'LRD'
        elif 'نامیبیا' in from_currency or 'namibia' in from_currency:
            from_code = 'NAD'
        elif 'فیجی' in from_currency or 'fiji' in from_currency:
            from_code = 'FJD'
        elif 'جامائیکا' in from_currency or 'jamaica' in from_currency:
            from_code = 'JMD'
        elif 'باهاما' in from_currency or 'bahamas' in from_currency:
            from_code = 'BSD'
        elif 'بلیز' in from_currency or 'belize' in from_currency:
            from_code = 'BZD'
        elif 'باربادوس' in from_currency or 'barbados' in from_currency:
            from_code = 'BBD'
        else:
            from_code = 'USD'  # Default to USD if no specific country
    
    # Rupees
    if 'روپیه' in from_currency or 'rupee' in from_currency:
        if 'پاکستان' in from_currency or 'pakistan' in from_currency:
            from_code = 'PKR'
        elif 'هند' in from_currency or 'india' in from_currency:
            from_code = 'INR'
        elif 'سریلانکا' in from_currency or 'sri lanka' in from_currency:
            from_code = 'LKR'
        elif 'نپال' in from_currency or 'nepal' in from_currency:
            from_code = 'NPR'
        elif 'اندونزی' in from_currency or 'indonesia' in from_currency:
            from_code = 'IDR'
        elif 'موریس' in from_currency or 'mauritius' in from_currency:
            from_code = 'MUR'
        elif 'سیشل' in from_currency or 'seychelles' in from_currency:
            from_code = 'SCR'
    
    # Dinars
    if 'دینار' in from_currency or 'dinar' in from_currency:
        if 'کویت' in from_currency or 'kuwait' in from_currency:
            from_code = 'KWD'
        elif 'بحرین' in from_currency or 'bahrain' in from_currency:
            from_code = 'BHD'
        elif 'عراق' in from_currency or 'iraq' in from_currency:
            from_code = 'IQD'
        elif 'اردن' in from_currency or 'jordan' in from_currency:
            from_code = 'JOD'
        elif 'لیبی' in from_currency or 'libya' in from_currency:
            from_code = 'LYD'
        elif 'الجزایر' in from_currency or 'algeria' in from_currency:
            from_code = 'DZD'
        elif 'تونس' in from_currency or 'tunisia' in from_currency:
            from_code = 'TND'
        elif 'صربستان' in from_currency or 'serbia' in from_currency:
            from_code = 'RSD'
    
    # Riyals
    if 'ریال' in from_currency or 'riyal' in from_currency:
        if 'سعودی' in from_currency or 'saudi' in from_currency:
            from_code = 'SAR'
        elif 'قطر' in from_currency or 'qatar' in from_currency:
            from_code = 'QAR'
        elif 'عمان' in from_currency or 'oman' in from_currency:
            from_code = 'OMR'
        elif 'یمن' in from_currency or 'yemen' in from_currency:
            from_code = 'YER'
        elif 'ایران' in from_currency or 'iran' in from_currency:
            from_code = 'IRR'
    
    # Dirhams
    if 'درهم' in from_currency or 'dirham' in from_currency:
        if 'امارات' in from_currency or 'uae' in from_currency or 'emirates' in from_currency:
            from_code = 'AED'
        elif 'مراکش' in from_currency or 'morocco' in from_currency:
            from_code = 'MAD'
    
    # Pounds
    if 'پوند' in from_currency or 'pound' in from_currency:
        if 'انگلیس' in from_currency or 'بریتانیا' in from_currency or 'uk' in from_currency or 'british' in from_currency or 'sterling' in from_currency:
            from_code = 'GBP'
        elif 'مصر' in from_currency or 'egypt' in from_currency:
            from_code = 'EGP'
        elif 'سودان' in from_currency or 'sudan' in from_currency:
            from_code = 'SDG'
        elif 'لبنان' in from_currency or 'lebanon' in from_currency:
            from_code = 'LBP'
        elif 'سوریه' in from_currency or 'syria' in from_currency:
            from_code = 'SYP'
    
    # Francs
    if 'فرانک' in from_currency or 'franc' in from_currency:
        if 'سوئیس' in from_currency or 'swiss' in from_currency:
            from_code = 'CHF'
        elif 'رواندا' in from_currency or 'rwanda' in from_currency:
            from_code = 'RWF'
        elif 'جیبوتی' in from_currency or 'djibouti' in from_currency:
            from_code = 'DJF'
        elif 'بوروندی' in from_currency or 'burundi' in from_currency:
            from_code = 'BIF'
    
    # Pesos
    if 'پزو' in from_currency or 'peso' in from_currency:
        if 'مکزیک' in from_currency or 'mexico' in from_currency:
            from_code = 'MXN'
        elif 'فیلیپین' in from_currency or 'philippines' in from_currency:
            from_code = 'PHP'
        elif 'آرژانتین' in from_currency or 'argentina' in from_currency:
            from_code = 'ARS'
        elif 'شیلی' in from_currency or 'chile' in from_currency:
            from_code = 'CLP'
        elif 'کلمبیا' in from_currency or 'colombia' in from_currency:
            from_code = 'COP'
        elif 'کوبا' in from_currency or 'cuba' in from_currency:
            from_code = 'CUP'
        elif 'دومنیکن' in from_currency or 'dominican' in from_currency:
            from_code = 'DOP'
        elif 'اروگوئه' in from_currency or 'uruguay' in from_currency:
            from_code = 'UYU'
    
    # Same for target currency
    # Dollars
    if 'دلار' in to_currency or 'dollar' in to_currency:
        if 'کانادا' in to_currency or 'canada' in to_currency:
            to_code = 'CAD'
        elif 'استرالیا' in to_currency or 'australia' in to_currency:
            to_code = 'AUD'
        elif 'نیوزیلند' in to_currency or 'new zealand' in to_currency:
            to_code = 'NZD'
        elif 'سنگاپور' in to_currency or 'singapore' in to_currency:
            to_code = 'SGD'
        elif 'هنگ کنگ' in to_currency or 'hong kong' in to_currency:
            to_code = 'HKD'
        elif 'تایوان' in to_currency or 'taiwan' in to_currency:
            to_code = 'TWD'
        elif 'برونئی' in to_currency or 'brunei' in to_currency:
            to_code = 'BND'
        elif 'لیبریا' in to_currency or 'liberia' in to_currency:
            to_code = 'LRD'
        elif 'نامیبیا' in to_currency or 'namibia' in to_currency:
            to_code = 'NAD'
        elif 'فیجی' in to_currency or 'fiji' in to_currency:
            to_code = 'FJD'
        elif 'جامائیکا' in to_currency or 'jamaica' in to_currency:
            to_code = 'JMD'
        elif 'باهاما' in to_currency or 'bahamas' in to_currency:
            to_code = 'BSD'
        elif 'بلیز' in to_currency or 'belize' in to_currency:
            to_code = 'BZD'
        elif 'باربادوس' in to_currency or 'barbados' in to_currency:
            to_code = 'BBD'
        else:
            to_code = 'USD'  # Default to USD if no specific country
    
    # Rupees
    if 'روپیه' in to_currency or 'rupee' in to_currency:
        if 'پاکستان' in to_currency or 'pakistan' in to_currency:
            to_code = 'PKR'
        elif 'هند' in to_currency or 'india' in to_currency:
            to_code = 'INR'
        elif 'سریلانکا' in to_currency or 'sri lanka' in to_currency:
            to_code = 'LKR'
        elif 'نپال' in to_currency or 'nepal' in to_currency:
            to_code = 'NPR'
        elif 'اندونزی' in to_currency or 'indonesia' in to_currency:
            to_code = 'IDR'
        elif 'موریس' in to_currency or 'mauritius' in to_currency:
            to_code = 'MUR'
        elif 'سیشل' in to_currency or 'seychelles' in to_currency:
            to_code = 'SCR'
    
    # Dinars
    if 'دینار' in to_currency or 'dinar' in to_currency:
        if 'کویت' in to_currency or 'kuwait' in to_currency:
            to_code = 'KWD'
        elif 'بحرین' in to_currency or 'bahrain' in to_currency:
            to_code = 'BHD'
        elif 'عراق' in to_currency or 'iraq' in to_currency:
            to_code = 'IQD'
        elif 'اردن' in to_currency or 'jordan' in to_currency:
            to_code = 'JOD'
        elif 'لیبی' in to_currency or 'libya' in to_currency:
            to_code = 'LYD'
        elif 'الجزایر' in to_currency or 'algeria' in to_currency:
            to_code = 'DZD'
        elif 'تونس' in to_currency or 'tunisia' in to_currency:
            to_code = 'TND'
        elif 'صربستان' in to_currency or 'serbia' in to_currency:
            to_code = 'RSD'
    
    # Riyals
    if 'ریال' in to_currency or 'riyal' in to_currency:
        if 'سعودی' in to_currency or 'saudi' in to_currency:
            to_code = 'SAR'
        elif 'قطر' in to_currency or 'qatar' in to_currency:
            to_code = 'QAR'
        elif 'عمان' in to_currency or 'oman' in to_currency:
            to_code = 'OMR'
        elif 'یمن' in to_currency or 'yemen' in to_currency:
            to_code = 'YER'
        elif 'ایران' in to_currency or 'iran' in to_currency:
            to_code = 'IRR'
    
    # Dirhams
    if 'درهم' in to_currency or 'dirham' in to_currency:
        if 'امارات' in to_currency or 'uae' in to_currency or 'emirates' in to_currency:
            to_code = 'AED'
        elif 'مراکش' in to_currency or 'morocco' in to_currency:
            to_code = 'MAD'
    
    # Pounds
    if 'پوند' in to_currency or 'pound' in to_currency:
        if 'انگلیس' in to_currency or 'بریتانیا' in to_currency or 'uk' in to_currency or 'british' in to_currency or 'sterling' in to_currency:
            to_code = 'GBP'
        elif 'مصر' in to_currency or 'egypt' in to_currency:
            to_code = 'EGP'
        elif 'سودان' in to_currency or 'sudan' in to_currency:
            to_code = 'SDG'
        elif 'لبنان' in to_currency or 'lebanon' in to_currency:
            to_code = 'LBP'
        elif 'سوریه' in to_currency or 'syria' in to_currency:
            to_code = 'SYP'
    
    # Francs
    if 'فرانک' in to_currency or 'franc' in to_currency:
        if 'سوئیس' in to_currency or 'swiss' in to_currency:
            to_code = 'CHF'
        elif 'رواندا' in to_currency or 'rwanda' in to_currency:
            to_code = 'RWF'
        elif 'جیبوتی' in to_currency or 'djibouti' in to_currency:
            to_code = 'DJF'
        elif 'بوروندی' in to_currency or 'burundi' in to_currency:
            to_code = 'BIF'
    
    # Pesos
    if 'پزو' in to_currency or 'peso' in to_currency:
        if 'مکزیک' in to_currency or 'mexico' in to_currency:
            to_code = 'MXN'
        elif 'فیلیپین' in to_currency or 'philippines' in to_currency:
            to_code = 'PHP'
        elif 'آرژانتین' in to_currency or 'argentina' in to_currency:
            to_code = 'ARS'
        elif 'شیلی' in to_currency or 'chile' in to_currency:
            to_code = 'CLP'
        elif 'کلمبیا' in to_currency or 'colombia' in to_currency:
            to_code = 'COP'
        elif 'کوبا' in to_currency or 'cuba' in to_currency:
            to_code = 'CUP'
        elif 'دومنیکن' in to_currency or 'dominican' in to_currency:
            to_code = 'DOP'
        elif 'اروگوئه' in to_currency or 'uruguay' in to_currency:
            to_code = 'UYU'
    
    if not from_code:

        return
    
    if not to_code:

        return
    
    # Get currency data
    data = event.client.currency_data
    if not data:
        await event.respond('متاسفانه در حال حاضر امکان دریافت اطلاعات نرخ ارز وجود ندارد. ❌')
        return
    
    # Perform conversion
    result = await convert_currency(amount, from_code, to_code, data)
    
    # Check if we got an error instead of conversion result
    if isinstance(result, dict) and 'error' in result:
        # Silently ignore non-existent currencies
        error_type = result['error']
        if error_type in ['both_currencies_not_found', 'from_currency_not_found', 'to_currency_not_found']:
            # Don't respond - just ignore the request
            return
        else:
            # For other types of errors, still show a message
            await event.respond('❌ خطا در تبدیل ارز. لطفاً دوباره تلاش کنید.')
            return
    
    if not result:
        await event.respond('❌ خطا در تبدیل ارز. لطفاً دوباره تلاش کنید.')
        return
    
    converted_amount, from_name, to_name, from_price, to_price = result
    
    # Format the response - round to integers for whole numbers or 2 decimal places for fractions
    # Check if it's a whole number by comparing with its integer value
    if converted_amount == int(converted_amount):
        converted_amount = int(converted_amount)
    else:
        converted_amount = round(converted_amount, 2)
        
    if to_code == 'TOMAN':
        formatted_result = format_number(converted_amount)
        result_text = f"{formatted_result} تومان"
    elif from_code == 'TOMAN':
        formatted_result = format_number(converted_amount)
        result_text = f"{formatted_result} {to_name}"
    else:
        formatted_result = format_number(converted_amount)
        result_text = f"{formatted_result} {to_name}"
    
    # Get the actual exchange rate directly from the result of convert_currency
    # from_price and to_price are the actual prices in Toman
    if to_code == 'TOMAN':
        # For conversions to Toman, show the price of the source currency in Toman
        exchange_rate = from_price
    elif from_code == 'TOMAN':
        # For conversions from Toman, show how many units of target currency per Toman
        exchange_rate = 1/to_price
    else:
        # For other currency pairs, calculate the direct exchange rate
        exchange_rate = from_price / to_price
    
    # Round to 2 decimal places for most currencies, but use more for very small values
    if exchange_rate >= 0.01:
        exchange_rate = round(exchange_rate, 2)
    else:
        exchange_rate = round(exchange_rate, 6)
    
    # Create a clean, elegant message with the correct exchange rate display
    input_amount = int(amount) if amount == int(amount) else round(amount, 2)
    
    # For USD to TOMAN conversions, directly get the dollar price from the cache
    if from_code == 'USD' and to_code == 'TOMAN':
        # Find dollar in main currencies
        main_currencies = data.get('mainCurrencies', {}).get('data', [])
        dollar_price = None
        for currency in main_currencies:
            if currency.get('currencyName') == 'دلار':
                dollar_price = currency.get('livePrice')
                if isinstance(dollar_price, str):
                    dollar_price = float(dollar_price.replace(',', ''))
                break
        
        if dollar_price is not None:
            rate_display = f"1 {from_name} = {format_number(dollar_price)} {to_name}"
        else:
            rate_display = f"1 {from_name} = {format_number(exchange_rate)} {to_name}"
    else:
        # For other conversions, use the calculated exchange rate
        rate_display = f"1 {from_name} = {format_number(exchange_rate)} {to_name}"
    
    message = f"""💱 <b>تبدیل ارز</b>

<b>{format_number(input_amount)} {from_name}</b> = <b>{result_text}</b>

📊 نرخ تبدیل: <b>{rate_display}</b>
⏱ آخرین بروزرسانی: {data.get('lastUpdate', 'نامشخص')}"""
    
    # Create buttons for displaying information
    buttons = [
        [Button.url("📢 کانال ما", "https://t.me/TelebotCraft")],
        [Button.url("➕ افزودن ربات به گروه", f"https://t.me/{(await client.get_me()).username}?startgroup=true")]
    ]
    
    # Send with parse_mode to enable HTML formatting
    await event.respond(message, buttons=buttons, parse_mode='html')

async def convert_currency(amount, from_code, to_code, data):
    """Convert between currencies using the latest exchange rates"""
    # Special case: if both currencies are the same
    if from_code == to_code:
        return amount, get_currency_name(from_code), get_currency_name(to_code), 1, 1
    
    # Get currency rates in Toman
    from_price_toman = get_currency_price_in_toman(from_code, data)
    to_price_toman = get_currency_price_in_toman(to_code, data)
    
    # Check if we have rates for both currencies
    if from_price_toman is None and to_price_toman is None:
        return {'error': 'both_currencies_not_found', 'from_code': from_code, 'to_code': to_code}
    elif from_price_toman is None:
        return {'error': 'from_currency_not_found', 'currency': from_code}
    elif to_price_toman is None:
        return {'error': 'to_currency_not_found', 'currency': to_code}
    
    # Special case: if one of the currencies is Toman
    if from_code == 'TOMAN':
        converted_amount = amount / to_price_toman
        # For Toman to other currency, the exchange rate is the price of the target currency
        return converted_amount, 'تومان', get_currency_name(to_code), 1, to_price_toman
    
    if to_code == 'TOMAN':
        converted_amount = amount * from_price_toman
        # For other currency to Toman, the exchange rate is the price of the source currency
        return converted_amount, get_currency_name(from_code), 'تومان', from_price_toman, 1
    
    # Convert through Toman
    toman_amount = amount * from_price_toman
    converted_amount = toman_amount / to_price_toman
    
    # For currency to currency, calculate the direct exchange rate
    direct_rate = from_price_toman / to_price_toman
    
    return converted_amount, get_currency_name(from_code), get_currency_name(to_code), from_price_toman, to_price_toman

def get_currency_price_in_toman(currency_code, data):
    """Get the price of a currency in Toman"""
    if currency_code == 'TOMAN':
        return 1.0
    
    if currency_code == 'IRR':
        return 0.1  # 1 Toman = 10 Rials
    
    # For cryptocurrencies and precious metals, use USD as a fallback if not directly available
    crypto_and_metals = ['BTC', 'ETH', 'USDT', 'BNB', 'ADA', 'XRP', 'DOGE', 'DOT', 'SOL', 'SHIB', 'LTC', 'XAU', 'XAG', 'XPT', 'XPD']
    
    # Search in main currencies
    main_currencies = data.get('mainCurrencies', {}).get('data', [])
    for currency in main_currencies:
        if currency_matches_code(currency, currency_code):
            price = currency.get('livePrice')
            # Convert to float if it's a string
            if isinstance(price, str):
                try:
                    # Remove any commas and convert to float
                    price = float(price.replace(',', ''))
                    return price
                except ValueError:
                    continue
            elif price is not None:
                return price
    
    # Search in minor currencies
    minor_currencies = data.get('minorCurrencies', {}).get('data', [])
    for currency in minor_currencies:
        if currency_matches_code(currency, currency_code):
            price = currency.get('livePrice')
            # Convert to float if it's a string
            if isinstance(price, str):
                try:
                    # Remove any commas and convert to float
                    price = float(price.replace(',', ''))
                    return price
                except ValueError:
                    continue
            elif price is not None:
                return price
    
    # Fallback mechanism for currencies not found in the API data
    # Use approximate exchange rates for common currencies
    # These are rough estimates and should be updated periodically
    fallback_rates = {
        # Middle Eastern and Asian currencies
        'AFN': 0.5,      # Afghan Afghani
        'PKR': 0.15,     # Pakistani Rupee
        'INR': 0.5,      # Indian Rupee
        'BDT': 0.4,      # Bangladeshi Taka
        'LKR': 0.13,     # Sri Lankan Rupee
        'NPR': 0.3,      # Nepalese Rupee
        'BTN': 0.5,      # Bhutanese Ngultrum
        'MVR': 2.7,      # Maldivian Rufiyaa
        'IDR': 0.003,    # Indonesian Rupiah
        'MYR': 9.0,      # Malaysian Ringgit
        'SGD': 31.0,     # Singapore Dollar
        'BND': 31.0,     # Brunei Dollar
        'PHP': 0.75,     # Philippine Peso
        'MMK': 0.02,     # Myanmar Kyat
        'LAK': 0.002,    # Lao Kip
        'KHR': 0.01,     # Cambodian Riel
        'VND': 0.002,    # Vietnamese Dong
        'MNT': 0.01,     # Mongolian Tugrik
        
        # African currencies
        'EGP': 1.3,      # Egyptian Pound
        'DZD': 0.3,      # Algerian Dinar
        'MAD': 4.2,      # Moroccan Dirham
        'TND': 13.5,     # Tunisian Dinar
        'LYD': 8.5,      # Libyan Dinar
        'SDG': 0.07,     # Sudanese Pound
        'ETB': 0.75,     # Ethiopian Birr
        'KES': 0.32,     # Kenyan Shilling
        'UGX': 0.01,     # Ugandan Shilling
        'TZS': 0.02,     # Tanzanian Shilling
        'RWF': 0.04,     # Rwandan Franc
        'BIF': 0.02,     # Burundian Franc
        'SOS': 0.07,     # Somali Shilling
        'DJF': 0.23,     # Djiboutian Franc
        'GHS': 3.5,      # Ghanaian Cedi
        'NGN': 0.28,     # Nigerian Naira
        'ZAR': 2.3,      # South African Rand
        
        # Latin American currencies
        'BRL': 7.5,      # Brazilian Real
        'MXN': 1.8,      # Mexican Peso
        'ARS': 0.6,      # Argentine Peso
        'CLP': 0.5,      # Chilean Peso
        'COP': 0.1,      # Colombian Peso
        'PEN': 1.1,      # Peruvian Sol
        
        # Cryptocurrencies
        'BTC': 1200000000,  # Bitcoin
        'ETH': 80000000,    # Ethereum
        'USDT': 42000,      # Tether (approximately USD)
        'BNB': 15000000,    # Binance Coin
        'XRP': 20000,       # Ripple
        'ADA': 15000,       # Cardano
        'SOL': 3000000,     # Solana
        'DOGE': 5000,       # Dogecoin
        'DOT': 250000,      # Polkadot
        
        # Precious metals (per ounce)
        'XAU': 70000000,    # Gold
        'XAG': 800000,      # Silver
        'XPT': 35000000,    # Platinum
        'XPD': 40000000,    # Palladium
    }
    
    if currency_code in fallback_rates:
        return fallback_rates[currency_code]
    
    # For debugging purposes
    print(f"Currency not found: {currency_code}")
    return None

def currency_matches_code(currency_data, code):
    """Check if the currency data matches the given code"""
    name = currency_data.get('currencyName', '').lower()
    symbol = currency_data.get('currencySymbol', '').lower()
    
    # Direct code match if available
    if currency_data.get('currencyCode', '').upper() == code:
        return True
    
    # Map currency names to codes for comparison
    if code == 'USD' and ('دلار' in name or 'dollar' in name or symbol == '$'):
        return True
    elif code == 'EUR' and ('یورو' in name or 'euro' in name or symbol == '€'):
        return True
    elif code == 'GBP' and ('پوند' in name or 'pound' in name or symbol == '£'):
        return True
    elif code == 'AED' and ('درهم' in name or 'dirham' in name or 'emirati' in name or 'uae' in name):
        return True
    elif code == 'TRY' and ('لیر' in name or 'lira' in name or 'turkish' in name):
        return True
    elif code == 'AFN' and ('افغانی' in name or 'afghani' in name or 'afghan' in name):
        return True
    elif code == 'CNY' and ('یوان' in name or 'yuan' in name or 'chinese' in name or 'china' in name):
        return True
    elif code == 'JPY' and ('ین' in name or 'yen' in name or 'japanese' in name or 'japan' in name):
        return True
    elif code == 'RUB' and ('روبل' in name or 'ruble' in name or 'russian' in name or 'russia' in name):
        return True
    elif code == 'CAD' and ('دلار کانادا' in name or 'canadian dollar' in name or 'canada' in name):
        return True
    elif code == 'AUD' and ('دلار استرالیا' in name or 'australian dollar' in name or 'australia' in name):
        return True
    elif code == 'INR' and ('روپیه هند' in name or 'indian rupee' in name or 'india' in name):
        return True
    elif code == 'PKR' and ('روپیه پاکستان' in name or 'pakistani rupee' in name or 'pakistan' in name):
        return True
    elif code == 'IQD' and ('دینار عراق' in name or 'iraqi dinar' in name or 'iraq' in name):
        return True
    elif code == 'SAR' and ('ریال سعودی' in name or 'saudi riyal' in name or 'saudi' in name):
        return True
    elif code == 'QAR' and ('ریال قطر' in name or 'qatari riyal' in name or 'qatar' in name):
        return True
    elif code == 'KWD' and ('دینار کویت' in name or 'kuwaiti dinar' in name or 'kuwait' in name):
        return True
    
    # Add more mappings as needed
    
    return False

def get_currency_name(code):
    """Get the display name for a currency code"""
    currency_names = {
        # Major currencies
        'USD': 'دلار',
        'EUR': 'یورو',
        'GBP': 'پوند',
        'AED': 'درهم',
        'TRY': 'لیر',
        'TOMAN': 'تومان',
        'IRR': 'ریال',
        'CAD': 'دلار کانادا',
        'AUD': 'دلار استرالیا',
        'NZD': 'دلار نیوزیلند',
        'CHF': 'فرانک سوئیس',
        'JPY': 'ین ژاپن',
        'CNY': 'یوان چین',
        'RUB': 'روبل روسیه',
        'INR': 'روپیه هند',
        'KRW': 'وون کره جنوبی',
        
        # Middle Eastern currencies
        'SAR': 'ریال سعودی',
        'QAR': 'ریال قطر',
        'OMR': 'ریال عمان',
        'BHD': 'دینار بحرین',
        'KWD': 'دینار کویت',
        'IQD': 'دینار عراق',
        'SYP': 'لیره سوریه',
        'LBP': 'لیره لبنان',
        'JOD': 'دینار اردن',
        'YER': 'ریال یمن',
        'AFN': 'افغانی',
        'PKR': 'روپیه پاکستان',
        
        # Asian currencies
        'BDT': 'تاکا بنگلادش',
        'LKR': 'روپیه سریلانکا',
        'NPR': 'روپیه نپال',
        'IDR': 'روپیه اندونزی',
        'MYR': 'رینگیت مالزی',
        'SGD': 'دلار سنگاپور',
        'THB': 'بات تایلند',
        'VND': 'دونگ ویتنام',
        'PHP': 'پزوی فیلیپین',
        
        # African currencies
        'EGP': 'پوند مصر',
        'ZAR': 'رند آفریقای جنوبی',
        'DZD': 'دینار الجزایر',
        'MAD': 'درهم مراکش',
        'TND': 'دینار تونس',
        'NGN': 'نایرا نیجریه',
        'GHS': 'سدی غنا',
        
        # Latin American currencies
        'BRL': 'رئال برزیل',
        'MXN': 'پزوی مکزیک',
        'ARS': 'پزوی آرژانتین',
        'CLP': 'پزوی شیلی',
        'COP': 'پزوی کلمبیا',
        'PEN': 'سول پرو',
        
        # Cryptocurrencies
        'BTC': 'بیت کوین',
        'ETH': 'اتریوم',
        'USDT': 'تتر',
        'BNB': 'بایننس کوین',
        'ADA': 'کاردانو',
        'XRP': 'ریپل',
        'DOGE': 'دوج کوین',
        'DOT': 'پولکادات',
        'SOL': 'سولانا',
        'SHIB': 'شیبا اینو',
        'LTC': 'لایت کوین',
        
        # Precious metals
        'XAU': 'انس طلا',
        'XAG': 'انس نقره',
        'XPT': 'انس پلاتین',
        'XPD': 'انس پالادیوم'
    }
    
    return currency_names.get(code, code)

async def show_conversion_help(event, client):
    """Show help message for currency conversion"""
    help_text = """
💱 راهنمای تبدیل ارز:

برای تبدیل به تومان، کافیست مقدار و نام ارز را بنویسید:
• `100 دلار`
• `50 usd`
• `۱۰۰ یورو`

برای تبدیل بین دو ارز، از فرمت زیر استفاده کنید:
`مقدار ارز_مبدا به ارز_مقصد`

مثال‌ها:
• `100 دلار به یورو`
• `500 تومان به یورو`
• `50 usd to eur`

ارزهای پشتیبانی شده:
• دلار (USD)
• یورو (EUR)
• پوند (GBP)
• درهم (AED)
• لیر (TRY)
• تومان (TOMAN)
• ریال (IRR)
و سایر ارزهای موجود در ربات
    """
    
    buttons = [
        [Button.inline("🏠 بازگشت به خانه", b'home')],
        [Button.url("📢 کانال ما", "https://t.me/TelebotCraft")]
    ]
    
    await event.respond(help_text, buttons=buttons)
