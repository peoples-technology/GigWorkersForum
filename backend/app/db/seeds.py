import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.db.models import Admin, FormVersion, Organisation, Platform, Setting, Unit

KERALA_DISTRICTS = [
    {"name": "Thiruvananthapuram", "name_ml": "തിരുവനന്തപുരം", "code": "KLTVC", "path": "kerala.tvm"},
    {"name": "Kollam", "name_ml": "കൊല്ലം", "code": "KLKLM", "path": "kerala.klm"},
    {"name": "Pathanamthitta", "name_ml": "പത്തനംതിട്ട", "code": "KLPTA", "path": "kerala.pta"},
    {"name": "Alappuzha", "name_ml": "ആലപ്പുഴ", "code": "KLALP", "path": "kerala.alp"},
    {"name": "Kottayam", "name_ml": "കോട്ടയം", "code": "KLKTM", "path": "kerala.ktm"},
    {"name": "Idukki", "name_ml": "ഇടുക്കി", "code": "KLIDK", "path": "kerala.idk"},
    {"name": "Ernakulam", "name_ml": "എറണാകുളം", "code": "KLEKM", "path": "kerala.ekm"},
    {"name": "Thrissur", "name_ml": "തൃശ്ശൂർ", "code": "KLTSR", "path": "kerala.tsr"},
    {"name": "Palakkad", "name_ml": "പാലക്കാട്", "code": "KLPKD", "path": "kerala.pkd"},
    {"name": "Malappuram", "name_ml": "മലപ്പുറം", "code": "KLMLP", "path": "kerala.mlp"},
    {"name": "Kozhikode", "name_ml": "കോഴിക്കോട്", "code": "KLKKD", "path": "kerala.kkd"},
    {"name": "Wayanad", "name_ml": "വയനാട്", "code": "KLWYD", "path": "kerala.wyd"},
    {"name": "Kannur", "name_ml": "കണ്ണൂർ", "code": "KLKNR", "path": "kerala.knr"},
    {"name": "Kasaragod", "name_ml": "കാസർഗോഡ്", "code": "KLKSD", "path": "kerala.ksd"},
]

DEFAULT_PLATFORMS = [
    {"id": "swiggy", "name": "Swiggy", "sector": "food_delivery"},
    {"id": "zomato", "name": "Zomato", "sector": "food_delivery"},
    {"id": "uber", "name": "Uber", "sector": "cab_mobility"},
    {"id": "ola", "name": "Ola", "sector": "cab_mobility"},
    {"id": "zepto", "name": "Zepto", "sector": "quick_commerce"},
    {"id": "blinkit", "name": "Blinkit", "sector": "quick_commerce"},
    {"id": "amazon_flex", "name": "Amazon Flex", "sector": "logistics"},
    {"id": "rapido", "name": "Rapido", "sector": "cab_mobility"},
    {"id": "porter", "name": "Porter", "sector": "logistics"},
]

CONFIRMED_15_FIELDS = [
    {
        "key": "full_name",
        "type": "text",
        "labels": {"en": "Full Name", "ml": "മുഴുവൻ പേര്"},
        "required": True,
    },
    {
        "key": "current_address",
        "type": "textarea",
        "labels": {"en": "Present Address", "ml": "നിലവിലെ മേൽവിലാസം"},
        "required": True,
    },
    {
        "key": "permanent_address",
        "type": "textarea",
        "labels": {"en": "Permanent Address (if different)", "ml": "സ്ഥിര മേൽവിലാസം"},
        "required": False,
    },
    {
        "key": "working_district",
        "type": "select",
        "labels": {"en": "Working District", "ml": "തൊഴിൽ ചെയ്യുന്ന ജില്ല"},
        "required": True,
        "options": [d["code"] for d in KERALA_DISTRICTS],
    },
    {
        "key": "email",
        "type": "email",
        "labels": {"en": "Email Address (Optional)", "ml": "ഇമെയിൽ (നിർബന്ധമില്ല)"},
        "required": False,
    },
    {
        "key": "mobile_number",
        "type": "phone",
        "labels": {"en": "Mobile Number", "ml": "മൊബൈൽ നമ്പർ"},
        "required": True,
    },
    {
        "key": "whatsapp_number",
        "type": "phone",
        "labels": {"en": "WhatsApp Number", "ml": "വാട്ട്സ്ആപ്പ് നമ്പർ"},
        "required": True,
    },
    {
        "key": "dob",
        "type": "date",
        "labels": {"en": "Date of Birth", "ml": "ജനന തീയതി"},
        "required": True,
        "validation": {"min_age": 18},
    },
    {
        "key": "gender",
        "type": "select",
        "labels": {"en": "Gender", "ml": "ലിംഗം"},
        "required": True,
        "options": ["male", "female", "transgender"],
    },
    {
        "key": "mother_tongue",
        "type": "text",
        "labels": {"en": "Mother Tongue", "ml": "മാതൃഭാഷ"},
        "required": True,
        "default": "Malayalam",
    },
    {
        "key": "platforms",
        "type": "multiselect",
        "labels": {"en": "Platforms Worked On", "ml": "തൊഴിലെടുക്കുന്ന പ്ലാറ്റ്‌ഫോമുകൾ"},
        "required": True,
    },
    {
        "key": "primary_platform",
        "type": "select",
        "labels": {"en": "Primary Platform", "ml": "പ്രധാന പ്ലാറ്റ്‌ഫോം"},
        "required": True,
    },
    {
        "key": "vehicle_type",
        "type": "select",
        "labels": {"en": "Vehicle Type", "ml": "വാഹന തരം"},
        "required": True,
        "options": ["motorcycle", "scooter_ev", "auto_rickshaw", "cab_car", "bicycle", "none"],
    },
    {
        "key": "vehicle_reg_no",
        "type": "text",
        "labels": {"en": "Vehicle Registration Number", "ml": "വാഹന രജിസ്ട്രേഷൻ നമ്പർ"},
        "required": False,
    },
    {
        "key": "id_doc_type",
        "type": "select",
        "labels": {"en": "ID Document Type", "ml": "തിരിച്ചറിയൽ രേഖ"},
        "required": True,
        "options": ["aadhaar", "driving_licence", "voter_id"],
    },
    {
        "key": "id_last4",
        "type": "text",
        "labels": {"en": "Last 4 Digits Only (DPDP Masked)", "ml": "അവസാന 4 അക്കങ്ങൾ മാത്രം"},
        "required": True,
        "validation": {"length": 4, "digits_only": True},
    },
]

DEFAULT_SETTINGS = [
    {
        "key": "module_autopay",
        "value": {"enabled": False},
        "description": "UPI Autopay mandate recurring subscription (deferred in pilot)",
    },
    {
        "key": "module_automated_lapse",
        "value": {"enabled": False, "grace_period_months": 6},
        "description": "Automatic membership lapse engine (off by default)",
    },
    {
        "key": "module_grievance_filing",
        "value": {"enabled": False, "contacts_display": True},
        "description": "Online grievance ticketing (contacts display only during pilot)",
    },
    {
        "key": "fee_structure",
        "value": {
            "registration_fee": 100,
            "monthly_fee": 10,
            "default_advance_months": 6,
            "total_initial_amount": 160,
        },
        "description": "Statutory pilot fee: Rs 100 registration + 6 months subscription (Rs 60)",
    },
]


async def seed_database(session: AsyncSession) -> None:
    # 1. Seed Organisation
    org_stmt = select(Organisation).limit(1)
    org_res = await session.execute(org_stmt)
    if not org_res.scalar_one_or_none():
        org = Organisation(
            name="Kerala State Gig & Platform Workers Union (CITU)",
            name_ml="കേരള സ്റ്റേറ്റ് ഗിഗ് & പ്ലാറ്റ്‌ഫോം വർക്കേഴ്സ് യൂണിയൻ (സി.ഐ.ടി.യു)",
            registration_number="CITU/KL/GIG/2026/04",
            default_language="ml",
        )
        session.add(org)

    # 2. Seed State Unit
    state_stmt = select(Unit).where(Unit.code == "KLSTATE")
    state_res = await session.execute(state_stmt)
    if not state_res.scalar_one_or_none():
        state_unit = Unit(
            name="Kerala State Committee",
            name_ml="കേരള സംസ്ഥാന കമ്മിറ്റി",
            code="KLSTATE",
            path="kerala",
            level="state",
        )
        session.add(state_unit)

    # 3. Seed 14 Districts
    for dist in KERALA_DISTRICTS:
        dist_stmt = select(Unit).where(Unit.code == dist["code"])
        dist_res = await session.execute(dist_stmt)
        if not dist_res.scalar_one_or_none():
            unit = Unit(
                name=dist["name"],
                name_ml=dist["name_ml"],
                code=dist["code"],
                path=dist["path"],
                level="district",
            )
            session.add(unit)

    # 4. Seed Platforms
    for p in DEFAULT_PLATFORMS:
        p_stmt = select(Platform).where(Platform.id == p["id"])
        p_res = await session.execute(p_stmt)
        if not p_res.scalar_one_or_none():
            platform = Platform(
                id=p["id"],
                name=p["name"],
                sector=p["sector"],
                is_active=True,
            )
            session.add(platform)

    # 5. Seed Form Version v1.0 with 15 confirmed fields
    fv_stmt = select(FormVersion).where(FormVersion.id == "v1.0")
    fv_res = await session.execute(fv_stmt)
    if not fv_res.scalar_one_or_none():
        fv = FormVersion(
            id="v1.0",
            name="Standard Registration v1.0 (15 Confirmed Fields)",
            fields=CONFIRMED_15_FIELDS,
            is_active=True,
        )
        session.add(fv)

    # 6. Seed Settings
    for s in DEFAULT_SETTINGS:
        setting_stmt = select(Setting).where(Setting.key == s["key"])
        setting_res = await session.execute(setting_stmt)
        if not setting_res.scalar_one_or_none():
            setting = Setting(
                key=s["key"],
                value=s["value"],
                description=s["description"],
            )
            session.add(setting)

    # 7. Seed Default State Admin (state_gs / CITUSolidarity@2026)
    admin_stmt = select(Admin).where(Admin.username == "state_gs")
    admin_res = await session.execute(admin_stmt)
    if not admin_res.scalar_one_or_none():
        state_unit_stmt = select(Unit).where(Unit.code == "KLSTATE")
        state_unit_res = await session.execute(state_unit_stmt)
        unit = state_unit_res.scalar_one_or_none()
        unit_id = unit.id if unit else uuid.uuid4()

        default_admin = Admin(
            id=uuid.UUID("99999999-9999-9999-9999-999999999999"),
            username="state_gs",
            name="Com. P. K. Sasidharan",
            email="gs@citu.kerala.org",
            role="state_admin",
            unit_id=unit_id,
            password_hash=hash_password("CITUSolidarity@2026"),
            totp_secret="JBSWY3DPEHPK3PXP",
            totp_enabled=True,
            recovery_codes=["REC001AA", "REC002BB", "REC003CC"],
            is_active=True,
        )
        session.add(default_admin)

    await session.commit()
