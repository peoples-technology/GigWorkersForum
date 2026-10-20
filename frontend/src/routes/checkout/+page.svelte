<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';

	let lang = $state<'ml' | 'en'>('ml');
	let activeTab = $state<'upi' | 'cards' | 'nb'>('upi');
	let selectedApp = $state<'gpay' | 'phonepe' | 'paytm' | 'bhim'>('gpay');
	let autopayEnabled = $state(true);
	let upiVpa = $state('anandhu@okaxis');

	// Card inputs
	let cardNumber = $state('');
	let cardExpiry = $state('');
	let cardCvv = $state('');

	// Netbanking inputs
	let selectedBank = $state('SBI');

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
			const pending = sessionStorage.getItem('pendingRegistration');
			if (pending) {
				const p = JSON.parse(pending);
				if (p.fullName) memberName = p.fullName.toUpperCase();
				if (p.district) memberDistrict = `${p.district} District`;
				if (p.primarySector || p.primaryPlatform) {
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
			generatedMemberId = `KL-${memberDistrict.includes('KL') ? memberDistrict.split('(')[1]?.replace(')', '') || 'TVC' : 'TVC'}-2026-${Math.floor(1000 + Math.random() * 9000)}`;
			paymentSuccess = true;
		}, 1300);
	}
</script>

<svelte:head>
	<title>{lang === 'ml' ? 'പേയ്മെന്റ് & ചെക്ക്ഔട്ട് | KSGPWU CITU' : 'Payment & Checkout | KSGPWU CITU'}</title>
</svelte:head>

<!-- Sticky Top Header -->
<header class="fixed top-0 w-full z-50 bg-surface-container-lowest border-b border-surface-variant shadow-[0_1px_3px_rgba(17,24,39,0.05),0_1px_2px_rgba(17,24,39,0.03)]">
	<div class="h-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between gap-4">
		<!-- Union Logo -->
		<a href="/" class="flex items-center gap-3 min-w-max hover:opacity-95 transition-opacity">
			<div class="w-10 h-10 rounded-lg bg-primary-container flex items-center justify-center text-on-primary shadow-sm flex-shrink-0 font-bold text-xl">
				★
			</div>
			<div class="flex flex-col">
				<span class="text-base sm:text-lg text-primary tracking-tight font-bold leading-tight">KSGPWU · CITU</span>
				<span class="text-xs text-secondary uppercase tracking-wider hidden sm:block">Kerala State Gig &amp; Platform Workers Union</span>
			</div>
		</a>

		<!-- Stepper Navigation -->
		<nav class="hidden md:flex items-center gap-2 text-xs font-semibold">
			<a href="/register" class="inline-flex items-center gap-1 px-3 py-1.5 rounded-full text-secondary hover:text-on-surface hover:bg-surface-container transition-all">
				<span>1. {lang === 'ml' ? 'രജിസ്ട്രേഷൻ' : 'Register'}</span>
				<span class="text-green-600 font-bold">✓</span>
			</a>
			<span class="text-secondary select-none">→</span>
			<span class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full shadow-sm bg-primary-container text-on-primary-container font-semibold">
				<span>2. {lang === 'ml' ? 'പേയ്മെന്റ്' : 'Payment'}</span>
				<span class="w-2 h-2 rounded-full bg-surface-container-lowest animate-pulse"></span>
			</span>
			<span class="text-secondary select-none">→</span>
			<span class="inline-flex items-center gap-1 px-3 py-1.5 rounded-full text-secondary opacity-60">
				<span>3. {lang === 'ml' ? 'കാർഡ്' : 'ID Card'}</span>
			</span>
		</nav>

		<!-- Security Pill & Language Switcher -->
		<div class="flex items-center gap-2 sm:gap-3 min-w-max">
			<div class="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-surface-container border border-surface-variant text-secondary text-xs">
				<span class="material-symbols-outlined text-[16px] text-tertiary">lock</span>
				<span class="font-semibold tracking-wide">256-Bit SSL</span>
			</div>

			<div class="inline-flex items-center bg-surface-container-low border border-surface-variant rounded-full p-0.5">
				<button 
					type="button" 
					onclick={() => lang = 'ml'}
					class={`px-2.5 py-1 rounded-full text-xs font-semibold transition-colors ${lang === 'ml' ? 'bg-primary text-on-primary' : 'text-secondary hover:text-on-surface'}`}
				>
					മലയാളം
				</button>
				<button 
					type="button" 
					onclick={() => lang = 'en'}
					class={`px-2.5 py-1 rounded-full text-xs font-semibold transition-colors ${lang === 'en' ? 'bg-primary text-on-primary' : 'text-secondary hover:text-on-surface'}`}
				>
					EN
				</button>
			</div>
		</div>
	</div>
</header>

<main class="w-full pt-20 bg-surface min-h-[calc(100vh-80px)]">
	<div class="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<!-- Top Context Header -->
		<div class="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
			<div class="flex flex-col gap-1">
				<a href="/register" class="inline-flex items-center gap-1 text-xs text-secondary hover:text-primary transition-colors group w-max">
					<span class="material-symbols-outlined text-[16px] group-hover:-translate-x-0.5 transition-transform">arrow_back</span>
					<span class="underline underline-offset-4">{lang === 'ml' ? 'മുൻപത്തെ പേജ് / തിരികെ ഫോമിലേക്ക്' : 'Back to registration form'}</span>
				</a>
				<h1 class="text-2xl sm:text-3xl font-bold text-on-surface tracking-tight mt-1">
					{lang === 'ml' ? 'പേയ്മെന്റ് & ചെക്ക്ഔട്ട്' : 'Payment & Checkout'} 
					<span class="font-normal text-secondary text-lg sm:text-xl">/ ₹160</span>
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
				<section class="bg-surface-container-lowest rounded-xl p-5 shadow-sm border border-surface-variant relative overflow-hidden">
					<div class="flex items-center justify-between pb-3 mb-3 border-b border-surface-variant">
						<div class="flex items-center gap-1.5">
							<span class="material-symbols-outlined text-primary text-[20px]">badge</span>
							<h2 class="text-sm font-bold text-on-surface">
								{lang === 'ml' ? 'അപേക്ഷകന്റെ വിവരങ്ങൾ' : 'Applicant Details'}
							</h2>
						</div>
						<span class="inline-flex items-center gap-1 bg-surface-container px-2.5 py-1 rounded-full text-tertiary text-[11px] font-semibold">
							<span class="material-symbols-outlined text-[14px]">verified</span>
							<span>{lang === 'ml' ? 'പരിശോധിച്ചു' : 'Verified'}</span>
						</span>
					</div>

					<div class="flex items-center gap-4">
						<div class="relative flex-shrink-0">
							<img 
								alt={memberName} 
								class="w-16 h-16 rounded-full object-cover shadow-sm ring-2 ring-primary-fixed" 
								src={memberPhoto}
								onerror={(e) => {
									(e.currentTarget as HTMLImageElement).src = "https://lh3.googleusercontent.com/aida-public/AB6AXuAw3aryKMEN6bCfcCaYf0tt2COhyR_la4FZRRuZKukGXcifwrYhg3DQBUwDt9nJjZkvRL0bzXPp6MlTyU9PQK1_7hv5Gm1YlkfXLqN7EYTDPvWL1R-Dg4KTXvtMCz2xCUBLZN16l9UYjGt3vc7Yq6SGnhs5IrXMNA9R_Rdz5n0ovSZtqvKvgKGfDzhs2UckUwtAzIbJ2iDOsSz3s2eGHL8uOrURfh0HmdmEkbO7_vXcahXIaRh1fiK8Dg";
								}}
							/>
							<div class="absolute -bottom-1 -right-1 bg-surface-container-lowest rounded-full p-0.5 shadow-sm">
								<span class="material-symbols-outlined text-tertiary text-[16px] block">check_circle</span>
							</div>
						</div>

						<div class="flex flex-col min-w-0">
							<span class="text-base text-on-surface font-bold truncate">{memberName}</span>
							<div class="flex items-center gap-1.5 mt-1">
								<span class="font-mono text-[11px] bg-surface-container px-2 py-0.5 rounded text-on-surface font-semibold">
									{memberAppId}
								</span>
								<span class="text-secondary text-xs">· Kerala Unit</span>
							</div>
							<div class="flex items-center gap-1 text-xs text-secondary mt-1">
								<span class="material-symbols-outlined text-[15px] text-outline">location_on</span>
								<span class="truncate">{memberDistrict}</span>
							</div>
							<div class="flex items-center gap-1 text-xs text-secondary mt-0.5">
								<span class="material-symbols-outlined text-[15px] text-primary">two_wheeler</span>
								<span class="font-medium text-on-surface truncate">{memberSector}</span>
							</div>
						</div>
					</div>
				</section>

				<!-- Itemized Fee Summary Card -->
				<section class="bg-surface-container-lowest rounded-xl p-5 shadow-sm border border-surface-variant">
					<div class="flex items-center justify-between pb-3 mb-4 border-b border-surface-variant">
						<div class="flex items-center gap-1.5">
							<span class="material-symbols-outlined text-secondary text-[20px]">receipt_long</span>
							<h2 class="text-sm font-bold text-on-surface">
								{lang === 'ml' ? 'വരിസംഖ്യ വിവരങ്ങൾ' : 'Itemized Fee Breakdown'}
							</h2>
						</div>
						<span class="font-mono text-xs text-secondary bg-surface-container px-2 py-0.5 rounded">
							FY 2026-27
						</span>
					</div>

					<!-- Fee Table Breakdown -->
					<div class="flex flex-col gap-3">
						<!-- Row 1 -->
						<div class="flex items-start justify-between py-1">
							<div class="flex flex-col pr-2">
								<span class="text-xs font-semibold text-on-surface">
									{lang === 'ml' ? '1. യൂണിയൻ പ്രവേശന ഫീസ് (വൺ-ടൈം)' : '1. Union Admission Fee (One-time)'}
								</span>
								<span class="text-[11px] text-secondary">
									One-time registration &amp; union ledger setup
								</span>
							</div>
							<span class="text-sm font-bold text-on-surface">₹100.00</span>
						</div>

						<div class="h-px w-full bg-surface-variant opacity-60"></div>

						<!-- Row 2 -->
						<div class="flex items-start justify-between py-1">
							<div class="flex flex-col pr-2">
								<span class="text-xs font-semibold text-on-surface">
									{lang === 'ml' ? '2. പ്രതിമാസ വരിസംഖ്യ (6 മാസം മുൻകൂർ)' : '2. Monthly Subscription (6 Months Adv.)'}
								</span>
								<span class="text-[11px] text-secondary">₹10 / month × 6 months</span>
							</div>
							<span class="text-sm font-bold text-on-surface">₹60.00</span>
						</div>

						<!-- Benefit Callout -->
						<div class="bg-surface-container-high rounded-lg p-3 flex items-start gap-2.5 mt-2">
							<span class="material-symbols-outlined text-tertiary text-[20px] flex-shrink-0 mt-0.5">security</span>
							<div class="flex flex-col text-xs">
								<span class="font-bold text-on-surface">
									{lang === 'ml' ? 'ഡിജിറ്റൽ ഐഡി കാർഡ് & ആനുകൂല്യങ്ങൾ' : 'Digital ID Card & Legal Cell Benefits'}
								</span>
								<p class="text-secondary leading-snug mt-0.5">
									Includes Official CITU QR ID Card, Welfare Board representation, and 24/7 Legal Dispute Protection.
								</p>
							</div>
						</div>

						<!-- Total Block -->
						<div class="flex items-center justify-between pt-2 bg-surface-container-low p-3.5 rounded-lg mt-2">
							<div class="flex flex-col">
								<span class="text-xs font-bold uppercase tracking-wide text-on-surface">
									{lang === 'ml' ? 'ആകെ അടയ്ക്കേണ്ട തുക' : 'Total Payable Amount'}
								</span>
								<span class="text-[11px] text-secondary">Inclusive of all statutory taxes</span>
							</div>
							<div class="text-right">
								<div class="text-2xl font-bold text-primary tracking-tight">₹160</div>
								<span class="text-[10px] text-secondary">One-time processing</span>
							</div>
						</div>
					</div>
				</section>

				<!-- Union Guarantee Panel -->
				<div class="bg-surface-container-low rounded-xl p-4 border border-surface-variant flex items-start gap-3">
					<span class="material-symbols-outlined text-primary text-[22px] flex-shrink-0 mt-0.5">verified_user</span>
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
								<span class="material-symbols-outlined text-primary text-[22px]">lock</span>
								<h2 class="text-lg font-bold text-on-surface">
									{lang === 'ml' ? 'സുരക്ഷിത പേയ്മെന്റ് ഗേറ്റ്‌വേ' : 'Secure Payment Gateway'}
								</h2>
							</div>
							<span class="text-xs text-secondary mt-0.5">
								Authorized Gateway · NPCI / UPI / BBPS Compliant
							</span>
						</div>
						<div class="flex items-center gap-1.5 bg-surface-container px-3 py-1 rounded-full text-xs font-semibold text-secondary">
							<span class="material-symbols-outlined text-tertiary text-[16px]">verified</span>
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
								<span class="material-symbols-outlined text-[18px] text-primary">qr_code_2</span>
								<span>UPI</span>
							</button>

							<button 
								type="button"
								onclick={() => activeTab = 'cards'}
								class={`py-2 px-2 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1 ${activeTab === 'cards' ? 'bg-surface-container-lowest text-on-surface shadow-sm' : 'text-secondary hover:text-on-surface'}`}
							>
								<span class="material-symbols-outlined text-[18px]">credit_card</span>
								<span>Cards</span>
							</button>

							<button 
								type="button"
								onclick={() => activeTab = 'nb'}
								class={`py-2 px-2 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1 ${activeTab === 'nb' ? 'bg-surface-container-lowest text-on-surface shadow-sm' : 'text-secondary hover:text-on-surface'}`}
							>
								<span class="material-symbols-outlined text-[18px]">account_balance</span>
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
											<span class="material-symbols-outlined text-[14px]">check_circle</span> Verified
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
											<span class="material-symbols-outlined text-primary text-[24px] mb-1">payments</span>
											<span class="text-xs font-bold text-on-surface">Google Pay</span>
											<span class="text-[10px] text-primary font-medium">{selectedApp === 'gpay' ? 'Selected' : 'Instant'}</span>
										</button>

										<!-- PhonePe -->
										<button 
											type="button" 
											onclick={() => selectedApp = 'phonepe'}
											class={`flex flex-col items-center justify-center p-3 rounded-lg border transition-all text-center ${selectedApp === 'phonepe' ? 'border-primary bg-primary-fixed/30 ring-1 ring-primary' : 'border-surface-variant bg-surface-container hover:bg-surface-container-high'}`}
										>
											<span class="material-symbols-outlined text-secondary text-[24px] mb-1">send_to_mobile</span>
											<span class="text-xs font-bold text-on-surface">PhonePe</span>
											<span class="text-[10px] text-secondary font-medium">{selectedApp === 'phonepe' ? 'Selected' : 'Instant'}</span>
										</button>

										<!-- Paytm -->
										<button 
											type="button" 
											onclick={() => selectedApp = 'paytm'}
											class={`flex flex-col items-center justify-center p-3 rounded-lg border transition-all text-center ${selectedApp === 'paytm' ? 'border-primary bg-primary-fixed/30 ring-1 ring-primary' : 'border-surface-variant bg-surface-container hover:bg-surface-container-high'}`}
										>
											<span class="material-symbols-outlined text-secondary text-[24px] mb-1">account_balance_wallet</span>
											<span class="text-xs font-bold text-on-surface">Paytm UPI</span>
											<span class="text-[10px] text-secondary font-medium">{selectedApp === 'paytm' ? 'Selected' : 'Instant'}</span>
										</button>

										<!-- BHIM -->
										<button 
											type="button" 
											onclick={() => selectedApp = 'bhim'}
											class={`flex flex-col items-center justify-center p-3 rounded-lg border transition-all text-center ${selectedApp === 'bhim' ? 'border-primary bg-primary-fixed/30 ring-1 ring-primary' : 'border-surface-variant bg-surface-container hover:bg-surface-container-high'}`}
										>
											<span class="material-symbols-outlined text-secondary text-[24px] mb-1">currency_rupee</span>
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

						<!-- Autopay Mandate Card -->
						<div class="bg-surface-container rounded-lg p-4 border border-surface-variant">
							<label class="flex items-start gap-3 cursor-pointer select-none">
								<input 
									type="checkbox" 
									bind:checked={autopayEnabled} 
									class="mt-1 w-4 h-4 rounded text-primary focus:ring-primary accent-primary cursor-pointer flex-shrink-0"
								/>
								<div class="flex flex-col text-xs">
									<span class="font-bold text-on-surface">
										{lang === 'ml' ? 'ഓട്ടോ-പേ ആക്റ്റിവേറ്റ് ചെയ്യുക (ഓപ്ഷണൽ)' : 'Enable Autopay (₹10 / month)'}
									</span>
									<p class="text-secondary mt-0.5 leading-relaxed">
										{lang === 'ml'
											? 'ഭാവിയിലെ പ്രതിമാസ വരിസംഖ്യകൾ (₹10/മാസം) ഓട്ടോമാറ്റിക് ആയി അടയ്ക്കുക. എപ്പോൾ വേണമെങ്കിലും ഒറ്റ ക്ലിക്കിൽ റദ്ദാക്കാം. RBI e-mandate compliant.'
											: 'Autopay future monthly union dues (₹10/mo). Cancel anytime from union portal or UPI app.'}
									</p>
								</div>
							</label>
						</div>

						<!-- Primary CTA Button -->
						<div class="flex flex-col gap-2">
							<button 
								type="button" 
								onclick={handlePayment} 
								disabled={isProcessing}
								class="w-full min-h-[52px] py-3.5 px-6 rounded-xl bg-primary hover:bg-primary-container text-on-primary text-base font-bold shadow-md transition-all flex items-center justify-center gap-2 active:scale-[0.99] disabled:opacity-60"
							>
								{#if isProcessing}
									<span class="material-symbols-outlined animate-spin text-[20px]">progress_activity</span>
									<span>{lang === 'ml' ? 'പ്രോസസ്സ് ചെയ്യുന്നു...' : 'Processing Payment...'}</span>
								{:else}
									<span class="material-symbols-outlined text-[20px]">lock</span>
									<span>{lang === 'ml' ? '₹160 അടയ്ക്കുക / അംഗത്വം ആക്റ്റീവ് ചെയ്യുക' : 'Pay ₹160 & Activate Membership'}</span>
									<span class="material-symbols-outlined text-[20px]">arrow_forward</span>
								{/if}
							</button>

							<div class="flex items-center justify-between text-secondary text-[11px] px-1">
								<span>GSTIN: 32AABTK1140P1ZT</span>
								<span class="flex items-center gap-1 text-primary font-medium">
									<span class="material-symbols-outlined text-[14px]">security</span>
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
								Kerala State Gig and Platform Workers Union (Registration: KL-07-TU-2026). All subscriptions are deposited directly to the Union Welfare Reserve Account.
							</p>
						</div>
					</div>
				</div>

				<!-- Help Strip -->
				<div class="mt-4 p-4 bg-surface-container-lowest rounded-xl border border-surface-variant shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
					<div class="flex items-center gap-3">
						<div class="w-9 h-9 rounded-full bg-surface-container flex items-center justify-center text-primary flex-shrink-0">
							<span class="material-symbols-outlined text-[20px]">support_agent</span>
						</div>
						<div class="flex flex-col text-xs">
							<span class="font-bold text-on-surface">
								{lang === 'ml' ? 'പേയ്മെന്റ് സഹായം ആവശ്യമുണ്ടോ?' : 'Need Payment Assistance?'}
							</span>
							<span class="text-secondary">Union Helpline (8 AM - 8 PM): 0471-2334567 / 9447012345</span>
						</div>
					</div>
					<a href="tel:04712334567" class="px-3.5 py-1.5 rounded-full bg-surface-container hover:bg-surface-container-high text-on-surface text-xs font-semibold flex items-center gap-1">
						<span>Call Helpline</span>
						<span class="material-symbols-outlined text-[15px]">call</span>
					</a>
				</div>
			</div>
		</div>
	</div>
</main>

<!-- Success Receipt Modal -->
{#if paymentSuccess}
	<div class="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
		<div class="bg-surface-container-lowest max-w-md w-full rounded-2xl shadow-2xl border border-surface-variant p-6 sm:p-8 flex flex-col items-center text-center animate-in fade-in zoom-in duration-200">
			<!-- Success Badge -->
			<div class="w-16 h-16 rounded-full bg-green-100 text-green-700 flex items-center justify-center mb-4 shadow-inner">
				<span class="material-symbols-outlined text-4xl">check_circle</span>
			</div>

			<h3 class="text-xl font-bold text-on-surface">
				{lang === 'ml' ? 'പേയ്മെന്റ് വിജയകരം!' : 'Payment Successful!'}
			</h3>
			<p class="text-xs text-secondary mt-1">
				{lang === 'ml' ? 'നിങ്ങളുടെ അംഗത്വം വിജയകരമായി സജീവമാക്കി.' : 'Your official union membership is now active.'}
			</p>

			<!-- Receipt Box -->
			<div class="w-full bg-surface-container-low rounded-xl p-4 my-5 border border-surface-variant text-left text-xs space-y-2">
				<div class="flex justify-between pb-2 border-b border-surface-variant">
					<span class="text-secondary font-medium">{lang === 'ml' ? 'അംഗത്വ നമ്പർ' : 'Membership ID'}:</span>
					<span class="font-mono font-bold text-primary">{generatedMemberId}</span>
				</div>
				<div class="flex justify-between">
					<span class="text-secondary">{lang === 'ml' ? 'അംഗം' : 'Member Name'}:</span>
					<span class="font-bold text-on-surface">{memberName}</span>
				</div>
				<div class="flex justify-between">
					<span class="text-secondary">{lang === 'ml' ? 'തുക' : 'Amount Paid'}:</span>
					<span class="font-bold text-on-surface">₹160.00</span>
				</div>
				<div class="flex justify-between">
					<span class="text-secondary">{lang === 'ml' ? 'ഇടപാട് ഐഡി' : 'Transaction Ref'}:</span>
					<span class="font-mono text-secondary">{transactionId}</span>
				</div>
				<div class="flex justify-between">
					<span class="text-secondary">{lang === 'ml' ? 'സാധുത' : 'Valid Until'}:</span>
					<span class="font-semibold text-green-700">31 October 2027</span>
				</div>
			</div>

			<!-- Action Buttons -->
			<div class="w-full flex flex-col gap-2.5">
				<a 
					href={`/verify/${generatedMemberId}`} 
					class="w-full py-3 px-4 rounded-xl bg-primary hover:bg-primary-container text-on-primary text-sm font-semibold flex items-center justify-center gap-2 shadow-sm"
				>
					<span class="material-symbols-outlined text-[18px]">badge</span>
					<span>{lang === 'ml' ? 'ഡിജിറ്റൽ ഐഡി കാർഡ് കാണുക' : 'View Digital ID Card'}</span>
				</a>

				<button 
					type="button" 
					onclick={() => window.print()}
					class="w-full py-2.5 px-4 rounded-xl border border-surface-variant bg-surface-container-lowest text-secondary text-xs font-semibold hover:bg-surface-container flex items-center justify-center gap-1.5"
				>
					<span class="material-symbols-outlined text-[16px]">print</span>
					<span>{lang === 'ml' ? 'രസീത് പ്രിന്റ് ചെയ്യുക' : 'Print Form-II Receipt'}</span>
				</button>
			</div>
		</div>
	</div>
{/if}

<!-- Footer -->
<footer class="w-full bg-surface-container-lowest border-t border-surface-variant py-6 mt-12">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-secondary">
		<p>Kerala State Gig &amp; Platform Workers Union (affil. CITU) · Statutory Labour Protection &amp; Dignity</p>
		<div class="flex items-center gap-2">
			<span class="material-symbols-outlined text-[16px] text-primary">verified_user</span>
			<span class="font-semibold">Secure Payment Gateway</span>
		</div>
	</div>
</footer>
