import os
import json
import re


COMPREHENSIVE_CURRENCY_CONFIGS = [
    {'name': 'دلار', 'flag': '🇺🇸', 'triggers': ['Dollar', 'USD', 'Usd', 'dollar', 'usd', 'دلار', 'دلار آمریکا']},
    {'name': 'یورو', 'flag': '🇪🇺', 'triggers': ['EUR', 'Euro', 'Eur', 'euro', 'eur', 'یورو', 'یورو اروپا']},
    {'name': 'درهم امارات', 'flag': '🇦🇪', 'triggers': ['AED', 'Aed', 'DIRHAM', 'Dirham', 'aed', 'dirham', 'درهم', 'درهم امارات']},
    {'name': 'پوند انگلیس', 'flag': '🇬🇧', 'triggers': ['GBP', 'Gbp', 'POUND', 'Pound', 'gbp', 'pound', 'پوند', 'پوند انگلیس']},
    {'name': 'لیر ترکیه', 'flag': '🇹🇷', 'triggers': ['TRY', 'TRYL', 'Trl', 'try', 'tryl', 'لیر', 'لیر ترکیه']},
    {'name': 'دلار کانادا', 'flag': '🇨🇦', 'triggers': ['CAD', 'Cad', 'Canadian Dollar', 'cad', 'canadian dollar', 'دلار کانادا']},
    {'name': 'دلار استرالیا', 'flag': '🇦🇺', 'triggers': ['AUD', 'Aud', 'Australian Dollar', 'aud', 'australian dollar', 'دلار استرالیا']},
    {'name': 'یوان چین', 'flag': '🇨🇳', 'triggers': ['CNY', 'Cny', 'YUAN', 'Yuan', 'cny', 'yuan', 'یوان', 'یوان چین']},
    {'name': 'ین ژاپن (100 ین)', 'flag': '🇯🇵', 'triggers': ['JPY', 'Jpy', 'YEN', 'Yen', 'jpy', 'yen', 'ین ژاپن', 'ین ژاپن (100 ین)']},
    {'name': 'فرانک سوئیس', 'flag': '🇨🇭', 'triggers': ['CHF', 'Chf', 'SWISS FRANC', 'Swiss Franc', 'chf', 'swiss franc', 'فرانک سوئیس']},
    {'name': 'رینگیت مالزی', 'flag': '🇲🇾', 'triggers': ['MYR', 'Myr', 'RINGGIT', 'Ringgit', 'myr', 'ringgit', 'رینگیت', 'رینگیت مالزی']},
    {'name': 'بات تایلند', 'flag': '🇹🇭', 'triggers': ['THB', 'Thb', 'BAHT', 'Baht', 'baht', 'thb', 'بات', 'بات تایلند']},
    {'name': 'دلار سنگاپور', 'flag': '🇸🇬', 'triggers': ['SGD', 'Sgd', 'Singapore Dollar', 'sgd', 'singapore dollar', 'دلار سنگاپور']},
    {'name': 'دلار هنگ کنگ', 'flag': '🇭🇰', 'triggers': ['HKD', 'Hkd', 'Hong Kong Dollar', 'hkd', 'hong kong dollar', 'دلار هنگ کنگ']},
    {'name': 'روپیه هند', 'flag': '🇮🇳', 'triggers': ['INR', 'Inr', 'RUPEE', 'Rupee', 'inr', 'rupee', 'روپیه', 'روپیه هند']},
    {'name': 'وون کره جنوبی', 'flag': '🇰🇷', 'triggers': ['KRW', 'Krw', 'WON', 'Won', 'krw', 'won', 'وون', 'وون کره جنوبی']},
    {'name': 'کرون سوئد', 'flag': '🇸🇪', 'triggers': ['KRONA', 'Krona', 'SEK', 'Sek', 'krona', 'sek', 'کرون', 'کرون سوئد']},
    {'name': 'کرون نروژ', 'flag': '🇳🇴', 'triggers': ['NOK', 'Nok', 'nok', 'norwegian krone', 'کرون نروژ']},
    {'name': 'کرون دانمارک', 'flag': '🇩🇰', 'triggers': ['DKK', 'Dkk', 'danish krone', 'dkk', 'کرون دانمارک']},
    {'name': 'روبل روسیه', 'flag': '🇷🇺', 'triggers': ['RUB', 'RUBLE', 'Rub', 'Ruble', 'rub', 'ruble', 'روبل', 'روبل روسیه']},
    {'name': 'منات آذربایجان', 'flag': '🇦🇿', 'triggers': ['AZN', 'Azn', 'MANAT', 'Manat', 'azn', 'manat', 'منات', 'منات آذربایجان']},
    {'name': 'درام ارمنستان', 'flag': '🇦🇲', 'triggers': ['AMD', 'Amd', 'DRAM', 'Dram', 'amd', 'dram', 'درام', 'درام ارمنستان']},
    {'name': 'لاری گرجستان', 'flag': '🇬🇪', 'triggers': ['GEL', 'Gel', 'LARI', 'Lari', 'gel', 'lari', 'لاری', 'لاری گرجستان']},
    {'name': 'سوم قرقیزستان', 'flag': '🇰🇬', 'triggers': ['KGS', 'Kgs', 'SOM', 'Som', 'kgs', 'som', 'سوم', 'سوم قرقیزستان']},
    {'name': 'سامانی تاجیکستان', 'flag': '🇹🇯', 'triggers': ['SOMONI', 'Somoni', 'TJS', 'Tjs', 'somoni', 'tjs', 'سامانی', 'سامانی تاجیکستان']},
    {'name': 'سوم ازبکستان', 'flag': '🇺🇿', 'triggers': ['UZS', 'Uzs', 'سوم ازبکستان', 'uzbekistan som', 'uzs']},
    {'name': 'تنگه قزاقستان', 'flag': '🇰🇿', 'triggers': ['KZT', 'Kzt', 'TENGE', 'Tenge', 'kzt', 'tenge', 'تنگه', 'تنگه قزاقستان']},
    {'name': 'افغانی', 'flag': '🇦🇫', 'triggers': ['AFGHANI', 'AFN', 'Afghani', 'Afn', 'afghani', 'afn', 'افغانی', 'افغانی افغانستان']},
    {'name': 'روپیه پاکستان', 'flag': '🇵🇰', 'triggers': ['PKR', 'Pkr', 'pakistani rupee', 'pkr', 'روپیه پاکستان']},
    {'name': 'پوند سوریه', 'flag': '🇸🇾', 'triggers': ['SYP', 'Syp', 'لیره سوریه', 'پوند سوریه', 'syp', 'syrian pound']},
    {'name': 'دینار عراق', 'flag': '🇮🇶', 'triggers': ['IQD', 'Iqd', 'دینار عراق', 'iqd', 'iraqi dinar']},
    {'name': 'ریال عربستان', 'flag': '🇸🇦', 'triggers': ['SAR', 'SAUDI RIYAL', 'Sar', 'Saudi Riyal', 'sar', 'saudi riyal', 'ریال', 'ریال عربستان']},
    {'name': 'ریال قطر', 'flag': '🇶🇦', 'triggers': ['QAR', 'QATARI RIYAL', 'Qar', 'Qatari Riyal', 'qar', 'qatari riyal', 'ریال قطر']},
    {'name': 'دینار کویت', 'flag': '🇰🇼', 'triggers': ['KUWAITI DINAR', 'KWD', 'Kuwaiti Dinar', 'Kwd', 'kwd', 'kuwaiti dinar', 'دینار کویت']},
    {'name': 'دینار بحرین', 'flag': '🇧🇭', 'triggers': ['BAHRAINI DINAR', 'BHD', 'Bahraini Dinar', 'Bhd', 'bahraini dinar', 'bhd', 'دینار بحرین']},
    {'name': 'ریال عمان', 'flag': '🇴🇲', 'triggers': ['OMANI RIAL', 'OMR', 'Omani Rial', 'Omr', 'omani rial', 'omr', 'ریال عمان']},
    {'name': 'ریال یمن', 'flag': '🇾🇪', 'triggers': ['YER', 'YEMENI RIAL', 'Yemeni Rial', 'Yer', 'yer', 'yemeni rial', 'ریال یمن']},
    {'name': 'انس طلا', 'flag': '🌟', 'triggers': ['GOLD', 'Gold', 'اونس طلا', 'طلا', 'gold']},
    {'name': 'انس نقره', 'flag': '🥈', 'triggers': ['SILVER', 'Silver', 'اونس نقره', 'نقره', 'silver']},
    {'name': 'انس پلاتین', 'flag': '💠', 'triggers': ['PLATINUM', 'Platinum', 'اونس پلاتین', 'پلاتین', 'platinum']},
    {'name': 'انس پالادیوم', 'flag': '🔘', 'triggers': ['PALLADIUM', 'Palladium', 'اونس پالادیوم', 'پالادیوم', 'palladium']},
    {'name': 'بیت کوین', 'flag': '₿', 'triggers': ['BITCOIN', 'Bitcoin', 'bitcoin', 'btc', 'بیت کوین']},
    {'name': 'اتریوم', 'flag': 'Ξ', 'triggers': ['ETHEREUM', 'Ethereum', 'ethereum', 'eth', 'اتریوم']},
    {'name': 'تتر', 'flag': '₮', 'triggers': ['TETHER', 'Tether', 'tether', 'usdt', 'تتر']},
    {'name': 'بایننس کوین', 'flag': '🔶', 'triggers': ['BINANCE COIN', 'Binance Coin', 'binance coin', 'bnb', 'بایننس کوین']},
    {'name': 'کاردانو', 'flag': ' ADA', 'triggers': ['CARDANO', 'Cardano', 'ada', 'cardano', 'کاردانو']},
    {'name': 'ریپل', 'flag': ' XRP', 'triggers': ['RIPPLE', 'Ripple', 'ripple', 'xrp', 'ریپل']},
    {'name': 'دوج کوین', 'flag': 'Ð', 'triggers': ['DOGECOIN', 'Dogecoin', 'doge', 'dogecoin', 'دوج کوین']},
    {'name': 'پولکادات', 'flag': 'DOT', 'triggers': ['DOT', 'POLKADOT', 'Polkadot', 'dot', 'polkadot', 'پولکادات']},
    {'name': 'سولانا', 'flag': 'SOL', 'triggers': ['SOL', 'SOLANA', 'Solana', 'sol', 'solana', 'سولانا']},
    {'name': 'شیبا اینو', 'flag': 'SHIB', 'triggers': ['SHIB', 'SHIBA INU', 'Shiba Inu', 'shib', 'shiba inu', 'شیبا اینو']},
    {'name': 'لایت کوین', 'flag': 'Ł', 'triggers': ['LITECOIN', 'Litecoin', 'litecoin', 'ltc', 'لایت کوین']},
    {'name': 'ترون', 'flag': 'TRX', 'triggers': ['TRON', 'TRX', 'Tron', 'tron', 'trx', 'ترون']},
    {'name': 'آوالانچ', 'flag': 'AVAX', 'triggers': ['AVALANCHE', 'AVAX', 'Avalanche', 'avalanche', 'avax', 'آوالانچ']},
    {'name': 'چین لینک', 'flag': 'LINK', 'triggers': ['CHAINLINK', 'LINK', 'Chainlink', 'chainlink', 'link', 'چین لینک']},
    {'name': 'یونی سواپ', 'flag': 'UNI', 'triggers': ['UNI', 'UNISWAP', 'Uniswap', 'uni', 'uniswap', 'یونی سواپ']},
    {'name': 'کازماس', 'flag': 'ATOM', 'triggers': ['ATOM', 'COSMOS', 'Cosmos', 'atom', 'cosmos', 'کازماس']},
    {'name': 'مونرو', 'flag': 'XMR', 'triggers': ['MONERO', 'Monero', 'XMR', 'monero', 'xmr', 'مونرو']},
    {'name': 'اتریوم کلاسیک', 'flag': 'ETC', 'triggers': ['ETC', 'ETHEREUM CLASSIC', 'Ethereum Classic', 'ethereum classic', 'etc', 'اتریوم کلاسیک']},
    {'name': 'فایل کوین', 'flag': 'FIL', 'triggers': ['FIL', 'FILECOIN', 'Filecoin', 'filecoin', 'fil', 'فایل کوین']},
    {'name': 'بیر اتیوپی', 'flag': '🇪🇹', 'triggers': ['ETB', 'Ethiopian Birr', 'Etb', 'بیر اتیوپی', 'etb', 'ethiopian birr']},
    {'name': 'فرانک گینه', 'flag': '🇬🇳', 'triggers': ['GNF', 'Gnf', 'Guinean Franc', 'فرانک گینه', 'gnf', 'guinean franc']},
    {'name': 'گواتزال گواتمالا', 'flag': '🇬🇹', 'triggers': ['GTQ', 'Gtq', 'Guatemalan Quetzal', 'gtq', 'guatemalan quetzal', 'گواتزال گواتمالا']},
    {'name': 'دلار گویان', 'flag': '🇬🇾', 'triggers': ['GYD', 'Gyd', 'Guyanese Dollar', 'دلار گویان', 'guyanese dollar', 'gyd']},
    {'name': 'لمپیرا هندوراس', 'flag': '🇭🇳', 'triggers': ['HNL', 'Hnl', 'Honduran Lempira', 'honduran lempira', 'hnl', 'لمپیرا هندوراس']},
    {'name': 'گورده هایتی', 'flag': '🇭🇹', 'triggers': ['HTG', 'Haitian Gourde', 'Htg', 'htg', 'haitian gourde', 'گورده هایتی', 'گورد هائیتی']},
    {'name': 'روپیه اندونزی', 'flag': '🇮🇩', 'triggers': ['IDR', 'Idr', 'Indonesian Rupiah', 'idr', 'indonesian rupiah', 'روپیه اندونزی']},
    {'name': 'شکل جدید اسرائیل', 'flag': '🇮🇱', 'triggers': ['ILS', 'Ils', 'Israeli New Shekel', 'ils', 'israeli new shekel', 'شکل جدید اسرائیل']},
    {'name': 'دینار اردن', 'flag': '🇯🇴', 'triggers': ['JOD', 'Jod', 'Jordanian Dinar', 'دینار اردن', 'jod', 'jordanian dinar']},
    {'name': 'شیلینگ کنیا', 'flag': '🇰🇪', 'triggers': ['KES', 'Kenyan Shilling', 'Kes', 'kenyan shilling', 'kes', 'شیلینگ کنیا']},
    {'name': 'کیپ لائوس', 'flag': '🇱🇦', 'triggers': ['LAK', 'Lak', 'Lao Kip', 'kip', 'lao kip', 'کیپ لائوس']},
    {'name': 'پوند لبنان', 'flag': '🇱🇧', 'triggers': ['LBP', 'Lbp', 'Lebanese Pound', 'lbp', 'lebanese pound', 'پوند لبنان']},
    {'name': 'روپیه سریلانکا', 'flag': '🇱🇰', 'triggers': ['LKR', 'Lkr', 'Sri Lankan Rupee', 'lkr', 'sri lankan rupee', 'روپیه سریلانکا']},
    {'name': 'دلار لیبریا', 'flag': '🇱🇷', 'triggers': ['LRD', 'Lrd', 'Liberian Dollar', 'lrd', 'liberian dollar', 'دلار لیبریا']},
    {'name': 'لوتی لسوتو', 'flag': '🇱🇸', 'triggers': ['LSL', 'Lsl', 'Lesotho Loti', 'lesotho loti', 'lsl', 'لوتی لسوتو']},
    {'name': 'دینار لیبی', 'flag': '🇱🇾', 'triggers': ['LYD', 'Lyd', 'Libyan Dinar', 'دینار لیبی', 'libyan dinar', 'lyd']},
    {'name': 'درهم مراکش', 'flag': '🇲🇦', 'triggers': ['MAD', 'Mad', 'Moroccan Dirham', 'دزد', 'mad', 'moroccan dirham', 'درهم مراکش']},
    {'name': 'لئوی مولداوی', 'flag': '🇲🇩', 'triggers': ['MDL', 'Mdl', 'Moldovan Leu', 'leu', 'mdl', 'moldovan leu', 'لئوی مولداوی', 'لئو مولداوی']},
    {'name': 'آریاری مالاگاسی', 'flag': '🇲🇬', 'triggers': ['MGA', 'Malagasy Ariary', 'Mga', 'آریاری مالاگاسی', 'mga', 'malagasy ariary', 'آریاری ماداگاسکار']},
    {'name': 'دنار مقدونیه', 'flag': '🇲🇰', 'triggers': ['MKD', 'Macedonian Denar', 'Mkd', 'denar', 'macedonian denar', 'mkd', 'دنار مقدونیه']},
    {'name': 'کیات میانمار', 'flag': '🇲🇲', 'triggers': ['MMK', 'Mmk', 'Myanmar Kyat', 'kyat', 'mmk', 'myanmar kyat', 'کیات میانمار']},
    {'name': 'توگروگ مغولستان', 'flag': '🇲🇳', 'triggers': ['MNT', 'Mnt', 'Mongolian Tugrik', 'mnt', 'mongolian tugrik', 'tugrik', 'توگروگ مغولستان']},
    {'name': 'پاتاکای ماکائو', 'flag': '🇲🇴', 'triggers': ['MOP', 'Macanese Pataca', 'Mop', 'mop', 'macanese pataca', 'pataca', 'پاتاکای ماکائو', 'پاتاکا ماکائو']},
    {'name': 'اوگوئیای موریتانی', 'flag': '🇲🇷', 'triggers': ['MRU', 'Mauritanian Ouguiya', 'Mru', 'mauritanian ouguiya', 'mru', 'ouguiya', 'اوگوئیای موریتانی']},
    {'name': 'روپیه موریس', 'flag': '🇲🇺', 'triggers': ['MUR', 'Mauritian Rupee', 'Mur', 'mauritian rupee', 'mur', 'روپیه موریس']},
    {'name': 'روفیا مالدیو', 'flag': '🇲🇻', 'triggers': ['MVR', 'Maldivian Rufiyaa', 'Mvr', 'maldivian rufiyaa', 'mvr', 'rufiyaa', 'روفیا مالدیو']},
    {'name': 'کواچای مالاوی', 'flag': '🇲🇼', 'triggers': ['MWK', 'Malawian Kwacha', 'Mwk', 'kwacha', 'malawian kwacha', 'mwk', 'کواچای مالاوی', 'کواچا مالاوی']},
    {'name': 'پزوی مکزیک', 'flag': '🇲🇽', 'triggers': ['MXN', 'Mexican Peso', 'Mxn', 'mexican peso', 'mxn', 'پزوی مکزیک']},
    {'name': 'متیکال موزامبیک', 'flag': '🇲🇿', 'triggers': ['MZN', 'Metical', 'Mozambican Metical', 'Mzn', 'metical', 'mozambican metical', 'mzn', 'متیکال موزامبیک']},
    {'name': 'دلار نامیبیا', 'flag': '🇳🇦', 'triggers': ['NAD', 'Nad', 'Namibian Dollar', 'nad', 'namibian dollar', 'دلار نامیبیا', 'دلار نامبیا']},
    {'name': 'نیرا نیجریه', 'flag': '🇳🇬', 'triggers': ['NGN', 'Ngn', 'Nigerian Naira', 'naira', 'ngn', 'nigerian naira', 'نایرای نیجریه', 'نیرا نیجریه']},
    {'name': 'کوردوبا نیکاراگوئه', 'flag': '🇳🇮', 'triggers': ['NIO', 'Nicaraguan Córdoba', 'Nio', 'nicaraguan córdoba', 'nio', 'کوردوبای نیکاراگوئه', 'کوردوبا نیکاراگوئه']},
    {'name': 'روپیه نپال', 'flag': '🇳🇵', 'triggers': ['NPR', 'Nepalese Rupee', 'Npr', 'nepalese rupee', 'npr', 'روپیه نپال']},
    {'name': 'دلار نیوزیلند', 'flag': '🇳🇿', 'triggers': ['NZD', 'New Zealand Dollar', 'Nzd', 'new zealand dollar', 'nzd', 'دلار نیوزیلند']},
    {'name': 'بولبوئا پاناما', 'flag': '🇵🇦', 'triggers': ['PAB', 'Pab', 'Panamanian Balboa', 'balboa', 'pab', 'panamanian balboa', 'بالبوآ پاناما', 'بولبوئا پاناما']},
    {'name': 'نوئووسول پرو', 'flag': '🇵🇪', 'triggers': ['PEN', 'Pen', 'Peruvian Nuevo Sol', 'nuevo sol', 'pen', 'peruvian nuevo sol', 'نوئووسول پرو']},
    {'name': 'کینا پاپوا گینه نو', 'flag': '🇵🇬', 'triggers': ['PGK', 'Papua New Guinean Kina', 'Pgk', 'kina', 'papua new guinean kina', 'pgk', 'کینای پاپوآ گینه نو', 'کینا پاپوا گینه نو']},
    {'name': 'پزوی فیلیپین', 'flag': '🇵🇭', 'triggers': ['PHP', 'Philippine Peso', 'Php', 'philippine peso', 'php', 'پزوی فیلیپین']},
    {'name': 'زلوتی لهستان', 'flag': '🇵🇱', 'triggers': ['PLN', 'Pln', 'Polish Złoty', 'pln', 'polish złoty', 'złoty', 'زلوتی لهستان']},
    {'name': 'گورانی پاراگوئه', 'flag': '🇵🇾', 'triggers': ['PYG', 'Paraguayan Guaraní', 'Pyg', 'guaraní', 'paraguayan guaraní', 'pyg', 'گوارانی پاراگوئه', 'گورانی پاراگوئه']},
    {'name': 'لئو رومانی', 'flag': '🇷🇴', 'triggers': ['RON', 'Romanian Leu', 'Ron', 'leu', 'romanian leu', 'ron', 'لئوی رومانی', 'لئو رومانی']},
    {'name': 'دینار صربستان', 'flag': '🇷🇸', 'triggers': ['RSD', 'Rsd', 'Serbian Dinar', 'rsd', 'serbian dinar', 'دینار صربستان']},
    {'name': 'فرانک رواندا', 'flag': '🇷🇼', 'triggers': ['RWF', 'Rwandan Franc', 'Rwf', 'rwf', 'rwandan franc', 'فرانک رواندا']},
    {'name': 'دلار جزایر سلیمان', 'flag': '🇸🇧', 'triggers': ['SBD', 'Sbd', 'Solomon Islands Dollar', 'sbd', 'solomon islands dollar', 'دلار جزایر سلیمان']},
    {'name': 'روپیه سیشل', 'flag': '🇸🇨', 'triggers': ['SCR', 'Scr', 'Seychellois Rupee', 'rupee', 'scr', 'seychellois rupee', 'روپیه سیشل']},
    {'name': 'پوند سودان', 'flag': '🇸🇩', 'triggers': ['SDG', 'Sdg', 'Sudanese Pound', 'sdg', 'sudanese pound', 'پوند سودان']},
    {'name': 'لئون سیرالئون', 'flag': '🇸🇱', 'triggers': ['SLE', 'Sierra Leonean Leone', 'Sle', 'leone', 'sierra leonean leone', 'sle', 'لئون سیرالئون']},
    {'name': 'شیلینگ سومالی', 'flag': '🇸🇴', 'triggers': ['SOS', 'Somali Shilling', 'Sos', 'shilling', 'somali shilling', 'sos', 'شیلینگ سومالی']},
    {'name': 'دلار سورینام', 'flag': '🇸🇷', 'triggers': ['SRD', 'Srd', 'Surinamese Dollar', 'srd', 'surinamese dollar', 'دلار سورینام']},
    {'name': 'پوند جنوب سودان', 'flag': '🇸🇸', 'triggers': ['SSP', 'Ssp', 'South Sudanese Pound', 'south sudanese pound', 'ssp', 'پوند جنوب سودان']},
    {'name': 'دبرای سائوتومه و پرینسیپ', 'flag': '🇸🇹', 'triggers': ['STN', 'Stn', 'São Tomé and Príncipe Dobra', 'dobra', 'são tomé and príncipe dobra', 'stn', 'دبرای سائوتومه و پرینسیپ']},
    {'name': 'کولون السالوادور', 'flag': '🇸🇻', 'triggers': ['SVC', 'Salvadoran Colón', 'Svc', 'colón', 'salvadoran colón', 'svc', 'کولون سالوادور', 'کولون السالوادور']},
    {'name': 'لیلانگی سوازیلند', 'flag': '🇸🇿', 'triggers': ['SZL', 'Swazi Lilangeni', 'Szl', 'lilangeni', 'swazi lilangeni', 'szl', 'لیلانگنی سوازیلند', 'لیلانگی سوازیلند']},
    {'name': 'دلار جدید تایوان', 'flag': '🇹🇼', 'triggers': ['TWD', 'Twd', 'New Taiwan Dollar', 'new taiwan dollar', 'twd', 'دلار جدید تایوان']},
    {'name': 'شیلینگ تانزانیا', 'flag': '🇹🇿', 'triggers': ['TZS', 'Tanzanian Shilling', 'Tzs', 'shilling', 'tanzanian shilling', 'tzs', 'شیلینگ تانزانیا']},
    {'name': 'هریونای اوکراین', 'flag': '🇺🇦', 'triggers': ['UAH', 'Uah', 'Ukrainian Hryvnia', 'hryvnia', 'uah', 'ukrainian hryvnia', 'هریونای اوکراین']},
    {'name': 'شیلینگ اوگاندا', 'flag': '🇺🇬', 'triggers': ['UGX', 'Ugandan Shilling', 'Ugx', 'shilling', 'ugandan shilling', 'ugx', 'شیلینگ اوگاندا']},
    {'name': 'پزوی اروگوئه', 'flag': '🇺🇾', 'triggers': ['UYU', 'Uruguayan Peso', 'Uyu', 'uruguayan peso', 'uyu', 'پزوی اوروگوئه', 'پزوی اروگوئه']},
    {'name': 'بولیوار ونزوئلا', 'flag': '🇻🇪', 'triggers': ['VES', 'Venezuelan Bolívar Soberano', 'Ves', 'bolívar soberano', 'venezuelan bolívar soberano', 'ves', 'بولیوار ونزوئلا']},
    {'name': 'دونگ ویتنام', 'flag': '🇻🇳', 'triggers': ['VND', 'Vietnamese Đồng', 'Vnd', 'vnd', 'vietnamese đồng', 'đồng', 'دانگ ویتنام', 'دونگ ویتنام']},
    {'name': 'واتوی وانوآتو', 'flag': '🇻🇺', 'triggers': ['VUV', 'Vanuatu Vatu', 'Vuv', 'vanuatu vatu', 'vatu', 'vuv', 'واتوی وانوآتو']},
    {'name': 'تالای ساموآ', 'flag': '🇼🇸', 'triggers': ['WST', 'Wst', 'Samoan Tālā', 'samoan tālā', 'tālā', 'wst', 'تالای ساموآ']},
    {'name': 'فرانک سیفا آفریقای مرکزی', 'flag': '🌍', 'triggers': ['XAF', 'Xaf', 'xaf', 'central african cfa franc', 'فرانک سیفا آفریقای مرکزی']},
    {'name': 'دلار شرق کارائیب', 'flag': '🏝️', 'triggers': ['XCD', 'Xcd', 'xcd', 'east caribbean dollar', 'دلار شرق کارائیب']},
    {'name': 'فرانک سیفا آفریقای غربی', 'flag': '🌍', 'triggers': ['XOF', 'Xof', 'xof', 'west african cfa franc', 'فرانک سیفا آفریقای غربی']},
    {'name': 'فرانک اقیانوسیه', 'flag': '🇵🇫', 'triggers': ['XPF', 'Xpf', 'xpf', 'CFP Franc', 'cfp franc', 'franc pacifique', 'فرانک اقیانوسیه']},
    {'name': 'کواچا زامبیا', 'flag': '🇿🇲', 'triggers': ['ZMW', 'Zambian Kwacha', 'Zmw', 'kwacha', 'zambian kwacha', 'zmw', 'کواچای زامبیا', 'کواچا زامبیا']},
    {'name': 'دلار زیمبابوه', 'flag': '🇿🇼', 'triggers': ['ZWL', 'Zimbabwean Dollar', 'Zwl', 'zimbabwean dollar', 'zwl', 'دلار زیمبابوه']},
    {'name': 'منات ترکمنستان', 'flag': '🇹🇲', 'triggers': ['TMM', 'TMT', 'Tmm', 'Tmt', 'manat', 'tmm', 'tmt', 'turkmenistan manat', 'منات ترکمنستان']},
    {'name': 'لک آلبانی', 'flag': '🇦🇱', 'triggers': ['ALL', 'All', 'Albanian Lek', 'albanian lek', 'all', 'lek', 'لک آلبانی']},
    {'name': 'دلار باربادوس', 'flag': '🇧🇧', 'triggers': ['BBD', 'Barbadian Dollar', 'Bbd', 'barbadian dollar', 'bbd', 'دلار باربادوس']},
    {'name': 'تاکا بنگلادش', 'flag': '🇧🇩', 'triggers': ['BDT', 'Bangladeshi Taka', 'Bdt', 'bangladeshi taka', 'bdt', 'taka', 'تاکا بنگلادش']},
    {'name': 'لو بلغارستان', 'flag': '🇧🇬', 'triggers': ['BGN', 'Bulgarian Lev', 'Bgn', 'bulgarian lev', 'bgn', 'lev', 'لو بلغارستان']},
    {'name': 'فرانک بوروندی', 'flag': '🇧🇮', 'triggers': ['BIF', 'Bif', 'Burundian Franc', 'bif', 'burundian franc', 'فرانک بوروندی']},
    {'name': 'دلار برونئی', 'flag': '🇧🇳', 'triggers': ['BND', 'Brunei Dollar', 'Bnd', 'bnd', 'brunei dollar', 'دلار برونئی']},
    {'name': 'دلار باهاماس', 'flag': '🇧🇸', 'triggers': ['BSD', 'Bahamian Dollar', 'Bsd', 'bahamian dollar', 'bsd', 'دلار باهاماس']},
    {'name': 'پوله بوتسوانا', 'flag': '🇧🇼', 'triggers': ['BWP', 'Botswana Pula', 'Bwp', 'botswana pula', 'bwp', 'pula', 'پوله بوتسوانا']},
    {'name': 'روبل بلاروس', 'flag': '🇧🇾', 'triggers': ['BYN', 'Belarusian Ruble', 'Byn', 'belarusian ruble', 'byn', 'روبل بلاروس']},
    {'name': 'دلار بلیز', 'flag': '🇧🇿', 'triggers': ['BZD', 'Belize Dollar', 'Bzd', 'belize dollar', 'bzd', 'دلار بلیز']},
    {'name': 'پزوی کوبا', 'flag': '🇨🇺', 'triggers': ['CUP', 'Cuban Peso', 'Cup', 'cuban peso', 'cup', 'پزوی کوبا']},
    {'name': 'کرون چک', 'flag': '🇨🇿', 'triggers': ['CZK', 'Czech Koruna', 'Czk', 'czech koruna', 'czk', 'koruna', 'کرون چک']},
    {'name': 'فرانک جیبوتی', 'flag': '🇩🇯', 'triggers': ['DJF', 'Djf', 'Djiboutian Franc', 'djf', 'djiboutian franc', 'فرانک جیبوتی']},
    {'name': 'پزوی دومنیکن', 'flag': '🇩🇴', 'triggers': ['DOP', 'Dominican Peso', 'Dop', 'dominican peso', 'dop', 'پزوی دومنیکن']},
    {'name': 'دینار الجزایر', 'flag': '🇩🇿', 'triggers': ['DZD', 'Algerian Dinar', 'Dzd', 'algerian dinar', 'dzd', 'دینار الجزایر']},
    {'name': 'کونا کرواسی', 'flag': '🇭🇷', 'triggers': ['HRK', 'Croatian Kuna', 'Hrk', 'croatian kuna', 'hrk', 'kuna', 'کونا کرواسی']},
    {'name': 'کرونا ایسلند', 'flag': '🇮🇸', 'triggers': ['ISK', 'Icelandic Króna', 'Isk', 'icelandic króna', 'isk', 'króna', 'کرونا ایسلند']},
    {'name': 'دلار جامایکا', 'flag': '🇯🇲', 'triggers': ['JMD', 'Jamaican Dollar', 'Jmd', 'jamaican dollar', 'jmd', 'دلار جامایکا']},
    {'name': 'ریل کامبوج', 'flag': '🇰🇭', 'triggers': ['KHR', 'Cambodian Riel', 'Khr', 'cambodian riel', 'khr', 'riel', 'ریل کامبوج']},
    {'name': 'فرانک کومور', 'flag': '🇰🇲', 'triggers': ['KMF', 'Comorian Franc', 'Kmf', 'comorian franc', 'kmf', 'فرانک کومور']},
    {'name': 'دینار مقدونیه', 'flag': '🇲🇰', 'triggers': ['MKD', 'Macedonian Denar', 'Mkd', 'denar', 'macedonian denar', 'mkd', 'دینار مقدونیه']},
    {'name': 'اوگویا موریتانا', 'flag': '🇲🇷', 'triggers': ['MRU', 'Mauritanian Ouguiya', 'Mru', 'mauritanian ouguiya', 'mru', 'ouguiya', 'اوگویا موریتانا']},
    {'name': 'پوند سینت هلنا', 'flag': '🇸🇭', 'triggers': ['SHP', 'Saint Helena Pound', 'Shp', 'saint helena pound', 'shp', 'پوند سینت هلنا']},
    {'name': 'دینار تونس', 'flag': '🇹🇳', 'triggers': ['TND', 'Tunisian Dinar', 'Tnd', 'tnd', 'tunisian dinar', 'دینار تونس']},
    {'name': 'دلار ترینیداد و توباگو', 'flag': '🇹🇹', 'triggers': ['TTD', 'Trinidad and Tobago Dollar', 'Ttd', 'trinidad and tobago dollar', 'ttd', 'دلار ترینیداد و توباگو']},
    {'name': 'سدی غنا', 'flag': '🇬🇭', 'triggers': ['GHS', 'Ghanaian Cedi', 'Ghs', 'cedi', 'ghanaian cedi', 'ghs', 'سدی غنا']},
    {'name': 'سول پرو', 'flag': '🇵🇪', 'triggers': ['PEN', 'Peruvian Sol', 'Pen', 'peruvian sol', 'pen', 'sol', 'سول پرو']},
    {'name': 'پزوی شیلی', 'flag': '🇨🇱', 'triggers': ['CLP', 'Chilean Peso', 'Clp', 'chilean peso', 'clp', 'پزوی شیلی']},
    {'name': 'پوند مصر', 'flag': '🇪🇬', 'triggers': ['EGP', 'Egyptian Pound', 'Egp', 'egp', 'egyptian pound', 'پوند مصر']},
    {'name': 'رئال برزیل', 'flag': '🇧🇷', 'triggers': ['BRL', 'Brazilian Real', 'Brl', 'brl', 'brazilian real', 'real', 'رئال برزیل']},
    {'name': 'پزوی کلمبیا', 'flag': '🇨🇴', 'triggers': ['COP', 'Colombian Peso', 'Cop', 'clp', 'colombian peso', 'cop', 'پزوی کلمبیا']},
    {'name': 'پزوی آرژانتین', 'flag': '🇦🇷', 'triggers': ['ARS', 'Argentine Peso', 'Ars', 'argentine peso', 'ars', 'پزوی آرژانتین']},
    {'name': 'دلار جزایر کیمن', 'flag': '🇰🇾', 'triggers': ['KYD', 'Cayman Islands Dollar', 'Kyd', 'cayman islands dollar', 'kyd', 'دلار جزایر کیمن']},
    {'name': 'فورینت مجارستان', 'flag': '🇭🇺', 'triggers': ['HUF', 'Hungarian Forint', 'Huf', 'forint', 'huf', 'hungarian forint', 'فورینت مجارستان']},
    {'name': 'هریونیا اوکراین', 'flag': '🇺🇦', 'triggers': ['UAH', 'Uah', 'Ukrainian Hryvnia', 'hryvnia', 'uah', 'ukrainian hryvnia', 'هریونیا اوکراین']},
    {'name': 'رند آفریقای جنوبی', 'flag': '🇿🇦', 'triggers': ['ZAR', 'South African Rand', 'Zar', 'rand', 'south african rand', 'zar', 'رند آفریقای جنوبی']},
    {'name': 'دلار فیجی', 'flag': '🇫🇯', 'triggers': ['FJD', 'Fijian Dollar', 'Fjd', 'fijian dollar', 'fjd', 'دلار فیجی']},
    {'name': 'دلار تایوان', 'flag': '🇹🇼', 'triggers': ['TWD', 'New Taiwan Dollar', 'Twd', 'new taiwan dollar', 'twd', 'دلار تایوان']},
    {'name': 'فرانک آفریقای غربی', 'flag': '🌍', 'triggers': ['West African CFA Franc', 'XOF', 'Xof', 'west african cfa franc', 'xof', 'فرانک آفریقای غربی']},
    {'name': 'دلاسی گامبیا', 'flag': '🇬🇲', 'triggers': ['GMD', 'Gambian Dalasi', 'Gmd', 'dalasi', 'gambian dalasi', 'gmd', 'دلاسی گامبیا']},
    {'name': 'فرانک آفریقا', 'flag': '🌍', 'triggers': ['Central African CFA Franc', 'West African CFA Franc', 'XAF', 'XOF', 'Xaf', 'Xof', 'central african cfa franc', 'فرانک آفریقا', 'west african cfa franc', 'xaf', 'xof']},
    {'name': 'وانواتو واتو', 'flag': '🇻🇺', 'triggers': ['VUV', 'Vanuatu Vatu', 'Vuv', 'vanuatu vatu', 'vatu', 'vuv', 'وانواتو واتو']},
    {'name': 'آنتیل گیلدر هلند', 'flag': '🇳🇱', 'triggers': ['ANG', 'Antillean Guilder', 'Ang', 'ang', 'antillean guilder', 'guilder', 'آنتیل گیلدر هلند']},
    {'name': 'دوبرا سائوتومه و پرنسیپ', 'flag': '🇸🇹', 'triggers': ['STN', 'São Tomé and Príncipe Dobra', 'Stn', 'dobra', 'são tomé and príncipe dobra', 'stn', 'دوبرا سائوتومه و پرنسیپ']},
    {'name': 'دلار کارائیب شرقی', 'flag': '🌴', 'triggers': ['East Caribbean Dollar', 'XCD', 'Xcd', 'east caribbean dollar', 'xcd', 'دلار کارائیب شرقی']}
]

# Template for currency handler files
TEMPLATE = '''from telethon import events
from telethon.tl.custom import Button
from .utils import format_number, format_change

# Keywords that trigger this handler
TRIGGERS = {triggers}

async def handle_currency(event, client):
    """Handle {name} currency requests"""
    data = event.client.currency_data
    if not data:
        await event.respond('متاسفانه در حال حاضر امکان دریافت اطلاعات نرخ ارز وجود ندارد. ❌')
        return

    # Try main currencies first
    currencies = data.get('mainCurrencies', {{}}).get('data', [])
    currency_info = next((c for c in currencies if c['currencyName'] == '{name}'), None)
    
    # If not found in main currencies, try minor currencies
    if not currency_info:
        currencies = data.get('minorCurrencies', {{}}).get('data', [])
        currency_info = next((c for c in currencies if c['currencyName'] == '{name}'), None)
    
    if not currency_info:
        await event.respond('اطلاعات {name} در حال حاضر در دسترس نیست. ❌')
        return

    price = format_number(currency_info['livePrice'])
    change = format_change(currency_info['change'])
    lowest = format_number(currency_info['lowest'])
    highest = format_number(currency_info['highest'])
    time = currency_info['time']

    # Create buttons for displaying information
    buttons = [
        [Button.inline("💰 قیمت فعلی", b'noop'), Button.inline(f"{{price}} تومان", b'noop')],
        [Button.inline("📊 تغییرات", b'noop'), Button.inline(f"{{change}}", b'noop')],
        [Button.inline("⬇️ کمترین", b'noop'), Button.inline(f"{{lowest}}", b'noop')],
        [Button.inline("⬆️ بیشترین", b'noop'), Button.inline(f"{{highest}}", b'noop')],
        [Button.inline("🕒 بروزرسانی", b'noop'), Button.inline(f"{{time}}", b'noop')],
        [Button.url("📢 کانال ما", "https://t.me/TelebotCraft")],
        [Button.url("➕ افزودن ربات به گروه", f"https://t.me/{{(await client.get_me()).username}}?startgroup=true")]
    ]

    message = f"{flag} نرخ لحظه‌ای {name}:"
    await event.respond(message, buttons=buttons)
'''

def make_filename(name):
    """Convert currency name to a valid filename"""
    filename = name.replace(' ', '_')
    filename = re.sub(r'[\/:*?"<>|]', '', filename)
    return f"{filename}.py"

def generate_handlers():
    """Generate handler files for all currencies from generation_data.json"""
    try:
        with open('../generation_data.json', 'r', encoding='utf-8') as f:
            generation_data = json.load(f)
    except Exception as e:
        print(f"Error loading generation_data.json: {e}")
        return

    # Create a lookup map from the comprehensive config
    config_map = {item['name']: item for item in COMPREHENSIVE_CURRENCY_CONFIGS}

    currency_groups_to_process = []
    if 'mainCurrencies' in generation_data and 'data' in generation_data['mainCurrencies']:
        currency_groups_to_process.extend(generation_data['mainCurrencies']['data'])
    if 'minorCurrencies' in generation_data and 'data' in generation_data['minorCurrencies']:
        currency_groups_to_process.extend(generation_data['minorCurrencies']['data'])
    
    if not currency_groups_to_process:
        print("No currency data found in generation_data.json to process.")
        return

    for item in currency_groups_to_process:
        currency_name = item['currencyName']
        
        # Get config from the comprehensive map
        currency_config = config_map.get(currency_name)
        
        if not currency_config:
            print(f"Warning: No configuration found for '{currency_name}' in COMPREHENSIVE_CURRENCY_CONFIGS. Using defaults.")
            flag = '🌐'
            triggers = [currency_name]
        else:
            flag = currency_config.get('flag', '🌐')
            triggers = currency_config.get('triggers', [currency_name])
            # Ensure the currency name itself is always a trigger
            if currency_name not in triggers:
                triggers.insert(0, currency_name)
        
        filename = make_filename(currency_name)
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                handler_code = TEMPLATE.format(
                    name=currency_name,
                    flag=flag,
                    triggers=repr(triggers)
                )
                f.write(handler_code)
            print(f"Generated handler for {currency_name}")
        except Exception as e:
            print(f"Error generating handler for {currency_name}: {e}")
    
    print("Currency handlers generation complete!")

if __name__ == '__main__':
    generate_handlers() 