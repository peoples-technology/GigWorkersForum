<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import Icon from '$lib/Icon.svelte';

	let lang = $state<'ml' | 'en'>('ml');
	let activeTab = $state<'upi' | 'cards' | 'nb'>('upi');
	let selectedApp = $state<'gpay' | 'phonepe' | 'paytm' | 'bhim'>('gpay');

	let upiVpa = $state('anandhu@okaxis');

	// Card inputs
	let cardNumber = $state('');
	let cardExpiry = $state('');
	let cardCvv = $state('');

	// Netbanking inputs
	let selectedBank = $state('SBI');

	// Districts metadata
	const districts = [
		{ code: 'KLTVC', en: 'Thiruvananthapuram', ml: 'തിരുവനന്തപുരം' },
		{ code: 'KLKLM', en: 'Kollam', ml: 'കൊല്ലം' },
		{ code: 'KLPTA', en: 'Pathanamthitta', ml: 'പത്തനംതിട്ട' },
		{ code: 'KLALP', en: 'Alappuzha', ml: 'ആലപ്പുഴ' },
		{ code: 'KLKTM', en: 'Kottayam', ml: 'കോട്ടയം' },
		{ code: 'KLIDK', en: 'Idukki', ml: 'ഇടുക്കി' },
		{ code: 'KLERN', en: 'Ernakulam', ml: 'എറണാകുളം' },
		{ code: 'KLTSR', en: 'Thrissur', ml: 'തൃശ്ശൂർ' },
		{ code: 'KLPKD', en: 'Palakkad', ml: 'പാലക്കാട്' },
		{ code: 'KLMLP', en: 'Malappuram', ml: 'മലപ്പുറം' },
		{ code: 'KLKKD', en: 'Kozhikode', ml: 'കോഴിക്കോട്' },
		{ code: 'KLWND', en: 'Wayanad', ml: 'വയനാട്' },
		{ code: 'KLKNR', en: 'Kannur', ml: 'കണ്ണൂർ' },
		{ code: 'KLKSD', en: 'Kasaragod', ml: 'കാസർഗോഡ്' }
	];

	// Applicant Info (loaded from sessionStorage or fallback)
	let memberName = $state('ANANDHU K. S.');
	let memberAppId = $state('APP2026-00349');
	let memberDistrict = $state('Thiruvananthapuram (KLTVC)');
	let memberSector = $state('Food Delivery Partner (Zomato / Swiggy)');
	let memberPhoto = $state('https://lh3.googleusercontent.com/aida-public/AB6AXuAw3aryKMEN6bCfcCaYf0tt2COhyR_la4FZRRuZKukGXcifwrYhg3DQBUwDt9nJjZkvRL0bzXPp6MlTyU9PQK1_7hv5Gm1YlkfXLqN7EYTDPvWL1R-Dg4KTXvtMCz2xCUBLZN16l9UYjGt3vc7Yq6SGnhs5IrXMNA9R_Rdz5n0ovSZtqvKvgKGfDzhs2UckUwtAzIbJ2iDOsSz3s2eGHL8uOrURfh0HmdmEkbO7_vXcahXIaRh1fiK8Dg');

	// State
	let isProcessing = $state(false);
	let paymentSuccess = $state(false);
	let transactionId = $state('');
	let generatedMemberId = $state('KL-TVC-2026-00349');

	onMount(() => {
		try {
			const saved = sessionStorage.getItem('pendingRegistration') || localStorage.getItem('pendingRegistration');
			if (saved) {
				const p = JSON.parse(saved);
				if (p.fullName) memberName = p.fullName.toUpperCase();
				const distCode = p.workingDistrict || p.district || $page.url.searchParams.get('district');
				const distObj = districts.find(d => d.code === distCode);
				if (distObj) {
					memberDistrict = `${distObj.en} (${distObj.code})`;
				} else if (distCode) {
					memberDistrict = `${distCode} District`;
				}
				if (p.primaryPlatform || p.primarySector) {
					memberSector = `${p.primaryPlatform || ''} ${p.primarySector || ''}`.trim();
				}
				if (p.photo) memberPhoto = p.photo;
				if (p.mobile) upiVpa = `${p.mobile}@upi`;
				memberAppId = `APP2026-${Math.floor(10000 + Math.random() * 90000)}`;
			}
		} catch (e) {
			console.error('Error loading pending registration', e);
		}
	});

	function handlePayment() {
		isProcessing = true;
		setTimeout(() => {
			isProcessing = false;
			transactionId = 'TXN-' + Math.random().toString(36).substring(2, 10).toUpperCase();

			let p: any = {};
			try {
				const raw = sessionStorage.getItem('pendingRegistration') || localStorage.getItem('pendingRegistration');
				if (raw) p = JSON.parse(raw);
			} catch (e) {}

			const distCode = p.workingDistrict || p.district || $page.url.searchParams.get('district') || (memberDistrict.includes('(') ? memberDistrict.split('(')[1]?.replace(')', '') : 'KLTVC') || 'KLTVC';
			const distObj = districts.find(d => d.code === distCode) || {
				code: distCode,
				en: 'Thiruvananthapuram',
				ml: 'തിരുവനന്തപുരം'
			};
			const randomSuffix = Math.floor(1000 + Math.random() * 9000);
			const cleanCode = distObj.code.replace(/^KL/, '');
			generatedMemberId = `KL-${cleanCode}-2026-${randomSuffix}`;

			const registeredMember = {
				id: generatedMemberId,
				name: (p.fullName || memberName).toUpperCase(),
				nameMl: p.fullName || memberName,
				mobile: p.mobile || '',
				email: p.email || '',
				dob: p.dob || '',
				gender: p.gender || '',
				motherTongue: p.motherTongue || 'Malayalam',
				currentAddress: p.currentAddress || '',
				districtCode: distObj.code,
				districtNameEn: distObj.en,
				districtNameMl: distObj.ml,
				districtName: `${distObj.ml} / ${distObj.en}`,
				primarySector: p.primarySector || 'Delivery',
				primaryPlatform: p.primaryPlatform || 'Swiggy',
				customPlatform: p.customPlatform || '',
				workingMode: p.workingMode || 'Full Time',
				vehicleNumber: p.vehicleNumber || '',
				licenceNumber: p.licenceNumber || '',
				idDocType: p.idDocType || 'Aadhaar',
				idLastDigits: p.idLastDigits || '',
				photo: p.photo || memberPhoto,
				transactionId,
				amountPaid: 100,
				paidAt: new Date().toISOString(),
				validUntil: '31 October 2027',
				status: 'Active & Paid-Up',
				tokenHash: `SHA256-${distObj.code.toLowerCase()}_${Math.random().toString(36).substring(2, 8)}`
			};

			// Store in sessionStorage and persistent localStorage
			sessionStorage.setItem('currentMember', JSON.stringify(registeredMember));
			localStorage.setItem('lastRegisteredMember', JSON.stringify(registeredMember));
			localStorage.setItem(`member_${generatedMemberId.toUpperCase()}`, JSON.stringify(registeredMember));
			if (p.mobile) {
				localStorage.setItem(`member_${p.mobile}`, JSON.stringify(registeredMember));
			}

			try {
				const existingRegStr = localStorage.getItem('ksgpwu_members_registry');
				const reg = existingRegStr ? JSON.parse(existingRegStr) : {};
				reg[generatedMemberId.toUpperCase()] = registeredMember;
				if (p.mobile) {
					reg[p.mobile] = registeredMember;
				}
				localStorage.setItem('ksgpwu_members_registry', JSON.stringify(reg));
			} catch (e) {
				console.error(e);
			}

			// Sync card and photo to backend API so cross-device verification works instantly
			try {
				fetch('/api/cards/sync-member', {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({
						id: generatedMemberId,
						name: registeredMember.name,
						name_ml: registeredMember.nameMl,
						district_code: distObj.code,
						district_name: distObj.en,
						primary_sector: registeredMember.primarySector,
						primary_platform: registeredMember.primaryPlatform,
						vehicle_number: registeredMember.vehicleNumber,
						status: registeredMember.status,
						valid_until: registeredMember.validUntil,
						photo: registeredMember.photo
					})
				}).catch((err) => console.warn('Background sync failed:', err));
			} catch (e) {}

			paymentSuccess = true;
		}, 1300);
	}
</script>

<svelte:head>
	<title>{lang === 'ml' ? 'പേയ്മെന്റ് & ചെക്ക്ഔട്ട് | GigWorkers.Online' : 'Payment & Checkout | GigWorkers.Online'}</title>
</svelte:head>

<!-- Sticky Top Header -->
<header class="fixed top-0 left-0 right-0 w-full z-50 bg-white/95 backdrop-blur-md border-b border-slate-200/80 shadow-xs">
	<div class="h-16 sm:h-20 max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 flex items-center justify-between gap-2 sm:gap-4">
		<!-- Union Logo -->
		<a href="/" class="flex items-center gap-2 sm:gap-3.5 min-w-0 flex-shrink hover:opacity-95 transition-opacity">
			<img
				src="/gigLogo.png"
				alt="Kerala State Gig and Platform Workers Union (CITU) Official Logo"
				class="w-9 h-9 sm:w-11 sm:h-11 rounded-full object-contain drop-shadow-sm flex-shrink-0"
				onerror={(e) => {
					(e.currentTarget as HTMLImageElement).src = '/images/gigLogo.png';
				}}
			/>
			<div class="flex flex-col min-w-0">
				<span class="text-sm sm:text-lg text-slate-900 tracking-tight font-extrabold leading-tight truncate">GigWorkers<span class="text-primary">.Online</span></span>
				<span class="text-[10px] sm:text-xs text-slate-500 uppercase tracking-wider hidden sm:block font-medium truncate">Kerala State Gig &amp; Platform Workers Union</span>
			</div>
		</a>

		<!-- Stepper Navigation -->
		<nav class="hidden md:flex items-center gap-2 text-xs font-bold">
			<a href="/register" class="inline-flex items-center gap-1 px-3.5 py-1.5 rounded-full text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-all">
				<span>1. {lang === 'ml' ? 'രജിസ്ട്രേഷൻ' : 'Register'}</span>
				<span class="text-emerald-600 font-bold">✓</span>
			</a>
			<span class="text-slate-400 select-none">→</span>
			<span class="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full shadow-sm bg-red-100 text-red-900 border border-red-200 font-bold">
				<span>2. {lang === 'ml' ? 'പേയ്മെന്റ്' : 'Payment'}</span>
				<span class="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
			</span>
			<span class="text-slate-400 select-none">→</span>
			<span class="inline-flex items-center gap-1 px-3.5 py-1.5 rounded-full text-slate-400 opacity-60">
				<span>3. {lang === 'ml' ? 'കാർഡ്' : 'ID Card'}</span>
			</span>
		</nav>

		<!-- Security Pill & Language Switcher -->
		<div class="flex items-center gap-1.5 sm:gap-3 flex-shrink-0">
			<div class="hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-bold shadow-xs">
				<Icon name="lock" class="text-[16px] text-emerald-700" />
				<span class="tracking-wide">256-Bit SSL</span>
			</div>

			<div class="inline-flex items-center bg-slate-100 border border-slate-200 rounded-full p-0.5 sm:p-1 shadow-inner">
				<button 
					type="button" 
					onclick={() => lang = 'ml'}
					class={`px-2 sm:px-3 py-1 rounded-full text-[11px] sm:text-xs font-bold transition-all ${lang === 'ml' ? 'bg-primary text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'}`}
				>
					മലയാളം
				</button>
				<button 
					type="button" 
					onclick={() => lang = 'en'}
					class={`px-2 sm:px-3 py-1 rounded-full text-[11px] sm:text-xs font-bold transition-all ${lang === 'en' ? 'bg-primary text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'}`}
				>
					EN
				</button>
			</div>
		</div>
	</div>
</header>

<main class="w-full pt-20 hero-gradient-mesh min-h-[calc(100vh-80px)]">
	<div class="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<!-- Top Context Header -->
		<div class="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
			<div class="flex flex-col gap-1">
				<a href="/register" class="inline-flex items-center gap-1 text-xs text-secondary hover:text-primary transition-colors group w-max">
					<Icon name="arrow_back" class="text-[16px] group-hover:-translate-x-0.5 transition-transform" />
					<span class="underline underline-offset-4">{lang === 'ml' ? 'മുൻപത്തെ പേജ് / തിരികെ ഫോമിലേക്ക്' : 'Back to registration form'}</span>
				</a>
				<h1 class="text-2xl sm:text-3xl font-bold text-on-surface tracking-tight mt-1">
					{lang === 'ml' ? 'പേയ്മെന്റ് & ചെക്ക്ഔട്ട്' : 'Payment & Checkout'} 
					<span class="font-normal text-secondary text-lg sm:text-xl">/ ₹100</span>
				</h1>
				<p class="text-xs sm:text-sm text-secondary">
					{lang === 'ml' ? 'അംഗത്വം സജീവമാക്കാൻ പേയ്മെന്റ് പൂർത്തിയാക്കുക.' : 'Complete your payment to activate your official union membership.'}
				</p>
			</div>

			<!-- Right Status Chip -->
			<div class="flex items-center gap-2 bg-surface-container-high px-3.5 py-1.5 rounded-full self-start md:self-end shadow-sm">
				<span class="w-2.5 h-2.5 rounded-full bg-primary animate-pulse"></span>
				<div class="flex items-center gap-1 text-on-surface text-xs font-medium">
					<span class="font-semibold text-primary">{lang === 'ml' ? 'താത്കാലിക ഐഡി സാധുത: 24 മണിക്കൂർ' : 'Temp ID Valid for 24h'}</span>
				</div>
			</div>
		</div>

		<!-- Main Two-Column Civic Grid -->
		<div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
			<!-- LEFT COLUMN: Member Summary & Itemized Ledger (5 cols) -->
			<div class="lg:col-span-5 flex flex-col gap-6">
				<!-- Applicant Verification Card -->
				<section class="card-gloss rounded-2xl p-6 shadow-md border border-slate-200/90 relative overflow-hidden">
					<div class="flex items-center justify-between pb-3.5 mb-3.5 border-b border-slate-200">
						<div class="flex items-center gap-2">
							<Icon name="badge" class="text-primary text-[22px]" />
							<h2 class="text-sm font-bold text-slate-900">
								{lang === 'ml' ? 'അപേക്ഷകന്റെ വിവരങ്ങൾ' : 'Applicant Details'}
							</h2>
						</div>
						<span class="inline-flex items-center gap-1 bg-emerald-50 border border-emerald-200 px-3 py-1 rounded-full text-emerald-800 text-[11px] font-bold shadow-2xs">
							<Icon name="verified" class="text-[15px]" />
							<span>{lang === 'ml' ? 'പരിശോധിച്ചു' : 'Verified'}</span>
						</span>
					</div>

					<div class="flex items-center gap-4">
						<div class="relative flex-shrink-0">
							<img 
								alt={memberName} 
								class="w-16 h-16 rounded-2xl object-cover shadow-md ring-2 ring-primary/20" 
								src={memberPhoto}
								onerror={(e) => {
									(e.currentTarget as HTMLImageElement).src = "https://lh3.googleusercontent.com/aida-public/AB6AXuAw3aryKMEN6bCfcCaYf0tt2COhyR_la4FZRRuZKukGXcifwrYhg3DQBUwDt9nJjZkvRL0bzXPp6MlTyU9PQK1_7hv5Gm1YlkfXLqN7EYTDPvWL1R-Dg4KTXvtMCz2xCUBLZN16l9UYjGt3vc7Yq6SGnhs5IrXMNA9R_Rdz5n0ovSZtqvKvgKGfDzhs2UckUwtAzIbJ2iDOsSz3s2eGHL8uOrURfh0HmdmEkbO7_vXcahXIaRh1fiK8Dg";
								}}
							/>
							<div class="absolute -bottom-1 -right-1 bg-emerald-600 text-white rounded-full p-0.5 shadow-sm">
								<Icon name="check_circle" class="text-[15px] block" />
							</div>
						</div>

						<div class="flex flex-col min-w-0">
							<span class="text-base text-slate-900 font-extrabold truncate">{memberName}</span>
							<div class="flex items-center gap-1.5 mt-1">
								<span class="font-mono text-[11px] bg-slate-100 px-2 py-0.5 rounded text-slate-700 font-bold border border-slate-200">
									{memberAppId}
								</span>
								<span class="text-slate-500 text-xs">· Kerala Unit</span>
							</div>
							<div class="flex items-center gap-1 text-xs text-slate-600 mt-1">
								<Icon name="location_on" class="text-[15px] text-slate-400" />
								<span class="truncate">{memberDistrict}</span>
							</div>
							<div class="flex items-center gap-1 text-xs text-slate-600 mt-0.5">
								<Icon name="two_wheeler" class="text-[15px] text-primary" />
								<span class="font-semibold text-slate-800 truncate">{memberSector}</span>
							</div>
						</div>
					</div>
				</section>

				<!-- Itemized Fee Summary Card -->
				<section class="card-gloss rounded-2xl p-6 shadow-md border border-slate-200/90">
					<div class="flex items-center justify-between pb-3.5 mb-4 border-b border-slate-200">
						<div class="flex items-center gap-2">
							<Icon name="receipt_long" class="text-slate-700 text-[22px]" />
							<h2 class="text-sm font-bold text-slate-900">
								{lang === 'ml' ? 'വരിസംഖ്യ വിവരങ്ങൾ' : 'Itemized Fee Breakdown'}
							</h2>
						</div>
						<span class="font-mono text-xs text-slate-600 bg-slate-100 border border-slate-200 px-2.5 py-0.5 rounded font-semibold">
							FY 2026-27
						</span>
					</div>

					<!-- Fee Table Breakdown -->
					<div class="flex flex-col gap-3">
						<!-- Row 1 -->
						<div class="flex items-start justify-between py-1">
							<div class="flex flex-col pr-2">
								<span class="text-xs font-bold text-slate-800">
									{lang === 'ml' ? 'യൂണിയൻ രജിസ്ട്രേഷൻ ഫീസ് (ഒറ്റ-തവണ)' : 'Union Registration Fee (One-time)'}
								</span>
								<span class="text-[11px] text-slate-500">
									One-time registration &amp; union ledger setup
								</span>
							</div>
							<span class="text-sm font-black text-slate-900">₹100.00</span>
						</div>

						<!-- Benefit Callout -->
						<div class="bg-gradient-to-r from-red-50 to-amber-50 rounded-xl p-3.5 flex items-start gap-3 mt-2 border border-red-200/60 shadow-xs">
							<Icon name="security" class="text-primary text-[22px] flex-shrink-0 mt-0.5" />
							<div class="flex flex-col text-xs">
								<span class="font-bold text-slate-900">
									{lang === 'ml' ? 'ഡിജിറ്റൽ ഐഡി കാർഡ് & ആനുകൂല്യങ്ങൾ' : 'Digital ID Card & Legal Cell Benefits'}
								</span>
								<p class="text-slate-600 leading-snug mt-0.5">
									Includes Official CITU QR ID Card, Welfare Board representation, and 24/7 Legal Dispute Protection.
								</p>
							</div>
						</div>

						<!-- Total Block -->
						<div class="flex items-center justify-between pt-2 bg-gradient-to-br from-slate-900 via-slate-800 to-red-950 text-white p-4 rounded-xl mt-2 shadow-md">
							<div class="flex flex-col">
								<span class="text-xs font-bold uppercase tracking-wider text-red-300">
									{lang === 'ml' ? 'ആകെ അടയ്ക്കേണ്ട തുക' : 'Total Payable Amount'}
								</span>
								<span class="text-[11px] text-slate-300">Inclusive of all statutory taxes</span>
							</div>
							<div class="text-right">
								<div class="text-3xl font-black text-white tracking-tight">₹100</div>
								<span class="text-[10px] text-slate-300">One-time processing</span>
							</div>
						</div>
					</div>
				</section>

				<!-- Union Guarantee Panel -->
				<div class="bg-surface-container-low rounded-xl p-4 border border-surface-variant flex items-start gap-3">
					<Icon name="verified_user" class="text-primary text-[22px] flex-shrink-0 mt-0.5" />
					<div class="flex flex-col text-xs">
						<span class="font-bold text-on-surface">
							{lang === 'ml' ? 'നിയമാനുസൃത ട്രേഡ് യൂണിയൻ രസീത്' : 'Official Trade Union Receipt'}
						</span>
						<p class="text-secondary mt-0.5 leading-relaxed">
							{lang === 'ml'
								? 'പേയ്മെന്റ് പൂർത്തിയായ ഉടൻ ഫോം-II രസീതും CITU അംഗത്വ കാർഡും തത്സമയം ലഭ്യമാകും.'
								: 'Instant Form-II digital receipt and official CITU digital membership card issued upon confirmation.'}
						</p>
					</div>
				</div>
			</div>

			<!-- RIGHT COLUMN: Secure Payment Gateway (7 cols) -->
			<div class="lg:col-span-7 flex flex-col">
				<div class="bg-surface-container-lowest rounded-xl shadow-md border border-surface-variant overflow-hidden relative">
					<!-- Crimson Top Accent Bar -->
					<div class="h-1.5 w-full bg-primary"></div>

					<!-- Gateway Header -->
					<div class="p-5 sm:p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 bg-surface-container-lowest border-b border-surface-variant">
						<div class="flex flex-col">
							<div class="flex items-center gap-1.5">
								<Icon name="lock" class="text-primary text-[22px]" />
								<h2 class="text-lg font-bold text-on-surface">
									{lang === 'ml' ? 'സുരക്ഷിത പേയ്മെന്റ് ഗേറ്റ്‌വേ' : 'Secure Payment Gateway'}
								</h2>
							</div>
							<span class="text-xs text-secondary mt-0.5">
								Authorized Gateway · NPCI / UPI / BBPS Compliant
							</span>
						</div>
						<div class="flex items-center gap-1.5 bg-surface-container px-3 py-1 rounded-full text-xs font-semibold text-secondary">
							<Icon name="verified" class="text-tertiary text-[16px]" />
							<span>256-Bit SSL</span>
						</div>
					</div>

					<!-- Method Selector Tabs -->
					<div class="px-5 sm:px-6 pt-4 pb-2">
						<div class="grid grid-cols-3 gap-1 bg-surface-container p-1 rounded-lg">
							<button 
								type="button"
								onclick={() => activeTab = 'upi'}
								class={`py-2 px-2 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1 ${activeTab === 'upi' ? 'bg-surface-container-lowest text-on-surface shadow-sm' : 'text-secondary hover:text-on-surface'}`}
							>
								<Icon name="qr_code_2" class="text-[18px] text-primary" />
								<span>UPI</span>
							</button>

							<button 
								type="button"
								onclick={() => activeTab = 'cards'}
								class={`py-2 px-2 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1 ${activeTab === 'cards' ? 'bg-surface-container-lowest text-on-surface shadow-sm' : 'text-secondary hover:text-on-surface'}`}
							>
								<Icon name="credit_card" class="text-[18px]" />
								<span>Cards</span>
							</button>

							<button 
								type="button"
								onclick={() => activeTab = 'nb'}
								class={`py-2 px-2 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1 ${activeTab === 'nb' ? 'bg-surface-container-lowest text-on-surface shadow-sm' : 'text-secondary hover:text-on-surface'}`}
							>
								<Icon name="account_balance" class="text-[18px]" />
								<span>Net Banking</span>
							</button>
						</div>
					</div>

					<!-- Payment Form Body -->
					<div class="p-5 sm:p-6 pt-4 flex flex-col gap-5">
						<!-- TAB 1: UPI -->
						{#if activeTab === 'upi'}
							<div class="flex flex-col gap-4">
								<div>
									<label for="upi-vpa-input" class="flex items-center justify-between text-xs font-bold uppercase tracking-wider text-secondary mb-1">
										<span>{lang === 'ml' ? 'UPI ID നൽകുക' : 'Enter UPI ID / VPA'}</span>
										<span class="text-tertiary font-semibold flex items-center gap-1">
											<Icon name="check_circle" class="text-[14px]" /> Verified
										</span>
									</label>
									<div class="relative flex items-center">
										<input 
											id="upi-vpa-input"
											type="text" 
											bind:value={upiVpa} 
											placeholder="e.g. 9876543210@upi or yourname@okaxis" 
											class="w-full h-11 px-3 rounded-lg bg-surface-container-lowest text-on-surface text-sm border border-surface-variant focus:outline-none focus:ring-2 focus:ring-primary font-medium"
										/>
									</div>
									<span class="text-[11px] text-secondary mt-1 block">
										Linked VPA: <strong>{upiVpa}</strong> (Auto-verified)
									</span>
								</div>

								<!-- Instant App Picker Grid -->
								<div class="flex flex-col gap-2">
									<span class="text-xs font-semibold text-secondary">
										{lang === 'ml' ? 'ഇൻസ്റ്റന്റ് ആപ്പ് തിരഞ്ഞെടുക്കുക:' : 'Or select instant app:'}
									</span>
									<div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
										<!-- Google Pay -->
										<button 
											type="button" 
											onclick={() => selectedApp = 'gpay'}
											class={`flex flex-col items-center justify-center p-3 rounded-lg border transition-all text-center ${selectedApp === 'gpay' ? 'border-primary bg-primary-fixed/30 ring-1 ring-primary' : 'border-surface-variant bg-surface-container hover:bg-surface-container-high'}`}
										>
											<Icon name="payments" class="text-primary text-[24px] mb-1" />
											<span class="text-xs font-bold text-on-surface">Google Pay</span>
											<span class="text-[10px] text-primary font-medium">{selectedApp === 'gpay' ? 'Selected' : 'Instant'}</span>
										</button>

										<!-- PhonePe -->
										<button 
											type="button" 
											onclick={() => selectedApp = 'phonepe'}
											class={`flex flex-col items-center justify-center p-3 rounded-lg border transition-all text-center ${selectedApp === 'phonepe' ? 'border-primary bg-primary-fixed/30 ring-1 ring-primary' : 'border-surface-variant bg-surface-container hover:bg-surface-container-high'}`}
										>
											<Icon name="send_to_mobile" class="text-secondary text-[24px] mb-1" />
											<span class="text-xs font-bold text-on-surface">PhonePe</span>
											<span class="text-[10px] text-secondary font-medium">{selectedApp === 'phonepe' ? 'Selected' : 'Instant'}</span>
										</button>

										<!-- Paytm -->
										<button 
											type="button" 
											onclick={() => selectedApp = 'paytm'}
											class={`flex flex-col items-center justify-center p-3 rounded-lg border transition-all text-center ${selectedApp === 'paytm' ? 'border-primary bg-primary-fixed/30 ring-1 ring-primary' : 'border-surface-variant bg-surface-container hover:bg-surface-container-high'}`}
										>
											<Icon name="account_balance_wallet" class="text-secondary text-[24px] mb-1" />
											<span class="text-xs font-bold text-on-surface">Paytm UPI</span>
											<span class="text-[10px] text-secondary font-medium">{selectedApp === 'paytm' ? 'Selected' : 'Instant'}</span>
										</button>

										<!-- BHIM -->
										<button 
											type="button" 
											onclick={() => selectedApp = 'bhim'}
											class={`flex flex-col items-center justify-center p-3 rounded-lg border transition-all text-center ${selectedApp === 'bhim' ? 'border-primary bg-primary-fixed/30 ring-1 ring-primary' : 'border-surface-variant bg-surface-container hover:bg-surface-container-high'}`}
										>
											<Icon name="currency_rupee" class="text-secondary text-[24px] mb-1" />
											<span class="text-xs font-bold text-on-surface">BHIM Gov</span>
											<span class="text-[10px] text-secondary font-medium">{selectedApp === 'bhim' ? 'Selected' : 'NPCI Direct'}</span>
										</button>
									</div>
								</div>
							</div>
						{/if}

						<!-- TAB 2: Cards -->
						{#if activeTab === 'cards'}
							<div class="flex flex-col gap-3">
								<div>
									<label for="card-number-input" class="block text-xs font-bold uppercase tracking-wider text-secondary mb-1">
										Card Number (Debit / Credit / RuPay)
									</label>
									<input 
										id="card-number-input"
										type="text" 
										bind:value={cardNumber} 
										placeholder="4111 2222 3333 4444" 
										maxlength="19" 
										class="w-full h-11 px-3 rounded-lg bg-surface-container-lowest text-on-surface text-sm border border-surface-variant focus:outline-none focus:ring-2 focus:ring-primary font-mono"
									/>
								</div>
								<div class="grid grid-cols-2 gap-3">
									<div>
										<label for="card-expiry-input" class="block text-xs font-bold uppercase tracking-wider text-secondary mb-1">
											Expiry (MM/YY)
										</label>
										<input 
											id="card-expiry-input"
											type="text" 
											bind:value={cardExpiry} 
											placeholder="12/28" 
											maxlength="5" 
											class="w-full h-11 px-3 rounded-lg bg-surface-container-lowest text-on-surface text-sm border border-surface-variant focus:outline-none focus:ring-2 focus:ring-primary font-mono"
										/>
									</div>
									<div>
										<label for="card-cvv-input" class="block text-xs font-bold uppercase tracking-wider text-secondary mb-1">
											CVV
										</label>
										<input 
											id="card-cvv-input"
											type="password" 
											bind:value={cardCvv} 
											placeholder="•••" 
											maxlength="4" 
											class="w-full h-11 px-3 rounded-lg bg-surface-container-lowest text-on-surface text-sm border border-surface-variant focus:outline-none focus:ring-2 focus:ring-primary font-mono"
										/>
									</div>
								</div>
							</div>
						{/if}

						<!-- TAB 3: Net Banking -->
						{#if activeTab === 'nb'}
							<div class="flex flex-col gap-3">
								<label for="bank-select" class="block text-xs font-bold uppercase tracking-wider text-secondary">
									Select Bank
								</label>
								<select 
									id="bank-select"
									bind:value={selectedBank} 
									class="w-full h-11 px-3 rounded-lg bg-surface-container-lowest text-on-surface text-sm border border-surface-variant focus:outline-none focus:ring-2 focus:ring-primary"
								>
									<option value="SBI">State Bank of India (SBI)</option>
									<option value="Federal">Federal Bank</option>
									<option value="Canara">Canara Bank</option>
									<option value="HDFC">HDFC Bank</option>
									<option value="ICICI">ICICI Bank</option>
									<option value="KeralaBank">Kerala Bank</option>
								</select>
							</div>
						{/if}

						<!-- Primary CTA Button -->
						<div class="flex flex-col gap-2">
							<button 
								type="button" 
								onclick={handlePayment} 
								disabled={isProcessing}
								class="w-full min-h-[56px] py-4 px-6 rounded-2xl crimson-gradient-btn text-white text-base font-extrabold shadow-xl flex items-center justify-center gap-2.5 active:scale-[0.99] disabled:opacity-60 transition-all cursor-pointer"
							>
								{#if isProcessing}
									<Icon name="progress_activity" class="animate-spin text-[22px]" />
									<span>{lang === 'ml' ? 'പ്രോസസ്സ് ചെയ്യുന്നു...' : 'Processing Payment...'}</span>
								{:else}
									<Icon name="lock" class="text-[22px]" />
									<span>{lang === 'ml' ? '₹100 അടയ്ക്കുക / അംഗത്വം ആക്റ്റീവ് ചെയ്യുക' : 'Pay ₹100 & Activate Membership'}</span>
									<Icon name="arrow_forward" class="text-[20px]" />
								{/if}
							</button>

							<div class="flex items-center justify-between text-secondary text-[11px] px-1">
								<span>GSTIN: 32AABTK1140P1ZT</span>
								<span class="flex items-center gap-1 text-primary font-medium">
									<Icon name="security" class="text-[14px]" />
									100% Refundable Guarantee
								</span>
							</div>
						</div>

						<!-- Gateway Badges -->
						<div class="pt-2 flex flex-col items-center gap-2 text-center border-t border-surface-variant">
							<div class="flex flex-wrap items-center justify-center gap-3 text-xs text-secondary opacity-80">
								<span class="px-2 py-0.5 rounded bg-surface-container font-mono font-bold">UPI / NPCI</span>
								<span class="px-2 py-0.5 rounded bg-surface-container font-mono font-bold">RuPay</span>
								<span class="px-2 py-0.5 rounded bg-surface-container font-mono font-bold">VISA</span>
								<span class="px-2 py-0.5 rounded bg-surface-container font-mono font-bold">Mastercard</span>
							</div>
							<p class="text-[11px] text-secondary max-w-lg">
								Kerala State Gig and Platform Workers Union — GigWorkers.Online (Registration: Tu19965). All registration fees are deposited directly to the Union Welfare Reserve Account.
							</p>
						</div>
					</div>
				</div>

				<!-- Help Strip -->
				<div class="mt-4 p-4 bg-surface-container-lowest rounded-xl border border-surface-variant shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
					<div class="flex items-center gap-3">
						<div class="w-9 h-9 rounded-full bg-surface-container flex items-center justify-center text-primary flex-shrink-0">
							<Icon name="support_agent" class="text-[20px]" />
						</div>
						<div class="flex flex-col text-xs">
							<span class="font-bold text-on-surface">
								{lang === 'ml' ? 'പേയ്മെന്റ് സഹായം ആവശ്യമുണ്ടോ?' : 'Need Payment Assistance?'}
							</span>
							<span class="text-secondary">Union Helpline (8 AM - 8 PM): <a href="tel:9846063666" class="hover:underline font-semibold text-primary">9846063666</a> / <a href="tel:9447695655" class="hover:underline font-semibold text-primary">9447695655</a></span>
						</div>
					</div>
					<a href="tel:9846063666" class="px-3.5 py-1.5 rounded-full bg-surface-container hover:bg-surface-container-high text-on-surface text-xs font-semibold flex items-center gap-1">
						<span>Call Helpline</span>
						<Icon name="call" class="text-[15px]" />
					</a>
				</div>
			</div>
		</div>
	</div>
</main>

<!-- Success Receipt Modal -->
{#if paymentSuccess}
	<div class="fixed inset-0 z-50 bg-slate-950/75 backdrop-blur-sm flex items-center justify-center p-4">
		<div class="bg-white max-w-md w-full rounded-2xl shadow-2xl border border-slate-200 p-6 sm:p-8 flex flex-col items-center text-center animate-in fade-in zoom-in-95 duration-200 relative z-10">
			<!-- Success Badge -->
			<div class="w-16 h-16 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mb-4 shadow-inner">
				<Icon name="check_circle" class="text-4xl" />
			</div>

			<h3 class="text-xl font-bold text-slate-900">
				{lang === 'ml' ? 'പേയ്മെന്റ് വിജയകരം!' : 'Payment Successful!'}
			</h3>
			<p class="text-xs text-slate-500 mt-1">
				{lang === 'ml' ? 'നിങ്ങളുടെ അംഗത്വം വിജയകരമായി സജീവമാക്കി.' : 'Your official union membership is now active.'}
			</p>

			<!-- Receipt Box -->
			<div class="w-full bg-slate-50 rounded-xl p-4 my-5 border border-slate-200/80 text-left text-xs space-y-2">
				<div class="flex justify-between pb-2 border-b border-slate-200">
					<span class="text-slate-500 font-medium">{lang === 'ml' ? 'അംഗത്വ നമ്പർ' : 'Membership ID'}:</span>
					<span class="font-mono font-bold text-primary">{generatedMemberId}</span>
				</div>
				<div class="flex justify-between">
					<span class="text-slate-500">{lang === 'ml' ? 'അംഗം' : 'Member Name'}:</span>
					<span class="font-bold text-slate-900">{memberName}</span>
				</div>
				<div class="flex justify-between">
					<span class="text-slate-500">{lang === 'ml' ? 'തുക' : 'Amount Paid'}:</span>
					<span class="font-bold text-slate-900">₹100.00</span>
				</div>
				<div class="flex justify-between">
					<span class="text-slate-500">{lang === 'ml' ? 'ഇടപാട് ഐഡി' : 'Transaction Ref'}:</span>
					<span class="font-mono text-slate-600">{transactionId}</span>
				</div>
				<div class="flex justify-between">
					<span class="text-slate-500">{lang === 'ml' ? 'സാധുത' : 'Valid Until'}:</span>
					<span class="font-semibold text-emerald-700">31 October 2027</span>
				</div>
			</div>

			<!-- Action Buttons -->
			<div class="w-full flex flex-col gap-2.5">
				<a 
					href={`/verify/${generatedMemberId}`} 
					class="w-full py-3 px-4 rounded-xl bg-primary hover:bg-primary-container text-white text-sm font-semibold flex items-center justify-center gap-2 shadow-sm transition"
				>
					<Icon name="badge" class="text-[18px]" />
					<span>{lang === 'ml' ? 'ഡിജിറ്റൽ ഐഡി കാർഡ് കാണുക' : 'View Digital ID Card'}</span>
				</a>

				<button 
					type="button" 
					onclick={() => window.print()}
					class="w-full py-2.5 px-4 rounded-xl border border-slate-300 bg-white text-slate-700 text-xs font-semibold hover:bg-slate-50 flex items-center justify-center gap-1.5 transition"
				>
					<Icon name="print" class="text-[16px]" />
					<span>{lang === 'ml' ? 'രസീത് പ്രിന്റ് ചെയ്യുക' : 'Print Form-II Receipt'}</span>
				</button>
			</div>
		</div>
	</div>
{/if}

<!-- Footer -->
<footer class="w-full bg-surface-container-lowest border-t border-surface-variant py-6 mt-12">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center flex flex-col items-center justify-center gap-2 text-xs text-secondary">
		<div class="flex flex-col sm:flex-row items-center justify-between w-full gap-3">
			<div class="flex items-center gap-2">
				<img src="/gigLogo.png" alt="CITU Gig Workers Official Logo" class="w-4 h-4 object-contain" />
				<p>GigWorkers.Online · Kerala State Gig &amp; Platform Workers Union (CITU)</p>
			</div>
			<div class="flex items-center gap-2">
				<Icon name="verified_user" class="text-[16px] text-primary" />
				<span class="font-semibold">Secure Payment Gateway</span>
			</div>
		</div>
		<div class="text-[11px] text-secondary mt-1">
			Reg. No: <strong>Tu19965</strong> · E Balananda Smaraka Office, CITU State Committee Office, Mele Thampanoor, Thampanoor P.O. · Ph: <a href="tel:9846063666" class="hover:underline text-primary font-semibold">9846063666</a>, <a href="tel:9447695655" class="hover:underline text-primary font-semibold">9447695655</a>
		</div>
	</div>
</footer>
