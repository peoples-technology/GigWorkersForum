<script lang="ts">
	import { currentLanguage, translations } from '$lib/i18n';

	let lang = $state('ml');
	currentLanguage.subscribe((val) => {
		lang = val;
	});

	let currentStep = $state(1);

	// Form State
	let phone = $state('');
	let otp = $state('');
	let otpSent = $state(false);
	let mockOtp = $state('');
	let otpError = $state('');

	let fullName = $state('');
	let dob = $state('1998-05-14');
	let calculatedAge = $state(28);
	let gender = $state('male');
	let district = $state('KLEKM');
	let workingMode = $state('fulltime');
	let primaryPlatform = $state('Swiggy');
	let vehicleType = $state('Motorcycle');
	let vehicleNo = $state('KL-07-CC-4521');

	let idDocType = $state('Aadhaar');
	let idLast4 = $state('');
	let consentGiven = $state(false);
	let selfieCaptured = $state(true);

	// Completed State
	let membershipNumber = $state('KL-EKM-000042');

	const platforms = ['Swiggy', 'Zomato', 'Uber', 'Ola', 'Zepto', 'Amazon Flex', 'Rapido', 'Porter'];
	const districts = [
		{ code: 'KLTVC', name_en: 'Thiruvananthapuram', name_ml: 'തിരുവനന്തപുരം' },
		{ code: 'KLKLM', name_en: 'Kollam', name_ml: 'കൊല്ലം' },
		{ code: 'KLPTA', name_en: 'Pathanamthitta', name_ml: 'പത്തനംതിട്ട' },
		{ code: 'KLALP', name_en: 'Alappuzha', name_ml: 'ആലപ്പുഴ' },
		{ code: 'KLKTM', name_en: 'Kottayam', name_ml: 'കോട്ടയം' },
		{ code: 'KLIDK', name_en: 'Idukki', name_ml: 'ഇടുക്കി' },
		{ code: 'KLEKM', name_en: 'Ernakulam', name_ml: 'എറണാകുളം' },
		{ code: 'KLTSR', name_en: 'Thrissur', name_ml: 'തൃശ്ശൂർ' },
		{ code: 'KLPKD', name_en: 'Palakkad', name_ml: 'പാലക്കാട്' },
		{ code: 'KLMLP', name_en: 'Malappuram', name_ml: 'മലപ്പുറം' },
		{ code: 'KLKKD', name_en: 'Kozhikode', name_ml: 'കോഴിക്കോട്' },
		{ code: 'KLWYD', name_en: 'Wayanad', name_ml: 'വയനാട്' },
		{ code: 'KLKNR', name_en: 'Kannur', name_ml: 'കണ്ണൂർ' },
		{ code: 'KLKSD', name_en: 'Kasaragod', name_ml: 'കാസർഗോഡ്' }
	];

	function handleSendOtp() {
		if (phone.length < 10) {
			otpError = lang === 'ml' ? 'ശരിയായ മൊബൈൽ നമ്പർ നൽകുക' : 'Please enter a valid 10-digit mobile number';
			return;
		}
		otpSent = true;
		mockOtp = '123456';
		otp = '123456';
		otpError = '';
	}

	function handleVerifyOtp() {
		if (otp !== '123456') {
			otpError = lang === 'ml' ? 'തെറ്റായ ഒ.ടി.പി' : 'Invalid OTP code';
			return;
		}
		currentStep = 2;
	}

	function handleProceedToStep3() {
		if (!fullName) {
			fullName = lang === 'ml' ? 'രാഹുൽ കൃഷ്ണൻ' : 'Rahul Krishnan';
		}
		currentStep = 3;
	}

	function handleCompleteRegistration() {
		if (!idLast4) {
			idLast4 = '4821';
		}
		consentGiven = true;
		currentStep = 4;
	}
</script>

<div class="space-y-6">
	<!-- Progress Bar -->
	<div class="bg-white p-4 rounded-xl shadow-sm border border-slate-200">
		<div class="flex items-center justify-between text-xs font-semibold mb-2">
			<span class="text-citu-red">
				{lang === 'ml' ? `ഘട്ടം ${currentStep} / 4` : `Step ${currentStep} of 4`}
			</span>
			<span class="text-slate-500">
				{currentStep === 1
					? translations[lang as 'ml' | 'en'].step1
					: currentStep === 2
						? translations[lang as 'ml' | 'en'].step2
						: currentStep === 3
							? translations[lang as 'ml' | 'en'].step3
							: translations[lang as 'ml' | 'en'].step4}
			</span>
		</div>
		<div class="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
			<div
				class="bg-citu-red h-2.5 transition-all duration-300"
				style={`width: ${currentStep * 25}%`}
			></div>
		</div>
	</div>

	<!-- STEP 1: Phone & OTP -->
	{#if currentStep === 1}
		<div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-6">
			<!-- Solidarity Banner -->
			<div class="bg-red-50 border border-red-200 rounded-xl p-4 flex items-start space-x-3">
				<div class="text-citu-red text-2xl font-bold">✊</div>
				<div>
					<h2 class="text-sm font-bold text-citu-red leading-snug">
						{translations[lang as 'ml' | 'en'].tagline}
					</h2>
					<p class="text-xs text-slate-600 mt-1">
						{lang === 'ml'
							? 'സ്വിഗ്ഗി, സൊമാറ്റോ, ഊബർ, ഒല, സെപ്റ്റോ തൊഴിലാളികൾക്കായുള്ള ഔദ്യോഗിക യൂണിയൻ പ്ലാറ്റ്‌ഫോം.'
							: 'Official registration platform for Swiggy, Zomato, Uber, Ola, Zepto and platform workers.'}
					</p>
				</div>
			</div>

			<!-- Statutory Fee Notice -->
			<div class="bg-amber-50 border border-amber-200 text-amber-900 rounded-xl p-3 text-xs flex items-center justify-between font-medium">
				<span>{translations[lang as 'ml' | 'en'].feeNotice}</span>
				<span class="bg-amber-200/80 px-2 py-0.5 rounded font-bold">₹160</span>
			</div>

			<!-- Phone Input -->
			<div class="space-y-2">
				<label for="mobile-phone" class="block text-xs font-bold text-slate-700 uppercase tracking-wider">
					{translations[lang as 'ml' | 'en'].mobileLabel}
				</label>
				<div class="flex rounded-lg shadow-sm border border-slate-300 overflow-hidden focus-within:ring-2 focus-within:ring-citu-red">
					<span class="inline-flex items-center px-4 bg-slate-100 text-slate-600 font-semibold text-sm border-r border-slate-300">
						+91
					</span>
					<input
						id="mobile-phone"
						type="tel"
						bind:value={phone}
						placeholder={translations[lang as 'ml' | 'en'].mobilePlaceholder}
						class="flex-1 px-4 py-3 text-base focus:outline-none touch-target"
						maxlength="10"
					/>
				</div>
			</div>

			{#if !otpSent}
				<button
					onclick={handleSendOtp}
					class="w-full bg-citu-red hover:bg-citu-red-dark text-white font-bold py-3.5 px-4 rounded-xl shadow-md transition active:scale-98 touch-target flex items-center justify-center space-x-2"
				>
					<span>{translations[lang as 'ml' | 'en'].sendOtp}</span>
					<span>→</span>
				</button>
			{:else}
				<!-- OTP Entry -->
				<div class="space-y-3 pt-2 border-t border-slate-100">
					<div class="flex items-center justify-between">
						<label for="otp-code" class="text-xs font-bold text-slate-700">
							{translations[lang as 'ml' | 'en'].otpLabel}
						</label>
						<span class="text-xs text-citu-red font-medium">
							Mock OTP: {mockOtp}
						</span>
					</div>
					<input
						id="otp-code"
						type="text"
						bind:value={otp}
						class="w-full text-center tracking-[0.5em] font-mono text-2xl py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-citu-red focus:outline-none"
						maxlength="6"
					/>
					{#if otpError}
						<p class="text-xs text-red-600 font-medium">{otpError}</p>
					{/if}
					<button
						onclick={handleVerifyOtp}
						class="w-full bg-citu-red hover:bg-citu-red-dark text-white font-bold py-3.5 px-4 rounded-xl shadow-md transition active:scale-98 touch-target"
					>
						{translations[lang as 'ml' | 'en'].verifyOtp}
					</button>
				</div>
			{/if}
		</div>

	<!-- STEP 2: Profile & Platform -->
	{:else if currentStep === 2}
		<div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-5">
			<h2 class="text-base font-bold text-citu-slate border-b pb-2">
				{translations[lang as 'ml' | 'en'].step2}
			</h2>

			<!-- Full Name -->
			<div class="space-y-1">
				<label for="worker-name" class="block text-xs font-bold text-slate-700">
					{translations[lang as 'ml' | 'en'].fullName}
				</label>
				<input
					id="worker-name"
					type="text"
					bind:value={fullName}
					placeholder={lang === 'ml' ? 'ഉദാ: രാഹുൽ കൃഷ്ണൻ' : 'e.g. Rahul Krishnan'}
					class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-citu-red focus:outline-none text-sm touch-target"
				/>
			</div>

			<!-- DOB & Working District -->
			<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
				<div class="space-y-1">
					<label for="worker-dob" class="block text-xs font-bold text-slate-700">
						{translations[lang as 'ml' | 'en'].dob}
					</label>
					<input
						id="worker-dob"
						type="date"
						bind:value={dob}
						class="w-full px-3 py-2.5 border border-slate-300 rounded-lg text-sm touch-target"
					/>
					<span class="inline-block text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">
						✓ {calculatedAge} {translations[lang as 'ml' | 'en'].ageValid}
					</span>
				</div>

				<div class="space-y-1">
					<label for="worker-district" class="block text-xs font-bold text-slate-700">
						{translations[lang as 'ml' | 'en'].district}
					</label>
					<select
						id="worker-district"
						bind:value={district}
						class="w-full px-3 py-2.5 border border-slate-300 rounded-lg text-sm touch-target bg-white"
					>
						{#each districts as d}
							<option value={d.code}>
								{lang === 'ml' ? d.name_ml : d.name_en} ({d.code})
							</option>
						{/each}
					</select>
				</div>
			</div>

			<!-- Primary Platform Picker -->
			<div class="space-y-2">
				<span class="block text-xs font-bold text-slate-700">
					{translations[lang as 'ml' | 'en'].primaryPlatform}
				</span>
				<div class="flex flex-wrap gap-2">
					{#each platforms as p}
						<button
							type="button"
							onclick={() => (primaryPlatform = p)}
							class={`px-3 py-2 rounded-lg text-xs font-semibold border transition ${
								primaryPlatform === p
									? 'bg-citu-red text-white border-citu-red shadow-sm'
									: 'bg-slate-50 text-slate-700 border-slate-300 hover:bg-slate-100'
							}`}
						>
							{p}
						</button>
					{/each}
				</div>
			</div>

			<!-- Vehicle Details -->
			<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
				<div class="space-y-1">
					<label for="vehicle-type" class="block text-xs font-bold text-slate-700">
						{translations[lang as 'ml' | 'en'].vehicleType}
					</label>
					<select
						id="vehicle-type"
						bind:value={vehicleType}
						class="w-full px-3 py-2.5 border border-slate-300 rounded-lg text-sm touch-target bg-white"
					>
						<option value="Motorcycle">{lang === 'ml' ? 'ബൈക്ക് / മോട്ടോർസൈക്കിൾ' : 'Motorcycle'}</option>
						<option value="EV Scooter">{lang === 'ml' ? 'ഇ.വി സ്കൂട്ടർ' : 'EV Scooter'}</option>
						<option value="Auto Rickshaw">{lang === 'ml' ? 'ഓട്ടോറിക്ഷ' : 'Auto Rickshaw'}</option>
						<option value="Cab/Car">{lang === 'ml' ? 'ടാക്സി / കാർ' : 'Cab / Car'}</option>
						<option value="Bicycle">{lang === 'ml' ? 'സൈക്കിൾ' : 'Bicycle'}</option>
					</select>
				</div>

				<div class="space-y-1">
					<label for="vehicle-no" class="block text-xs font-bold text-slate-700">
						{translations[lang as 'ml' | 'en'].vehicleReg}
					</label>
					<input
						id="vehicle-no"
						type="text"
						bind:value={vehicleNo}
						placeholder="KL-07-CC-4521"
						class="w-full px-3 py-2.5 border border-slate-300 rounded-lg text-sm font-mono touch-target"
					/>
				</div>
			</div>

			<button
				onclick={handleProceedToStep3}
				class="w-full bg-citu-red hover:bg-citu-red-dark text-white font-bold py-3.5 px-4 rounded-xl shadow-md transition touch-target"
			>
				{lang === 'ml' ? 'അടുത്ത ഘട്ടത്തിലേക്ക് →' : 'Continue to Verification →'}
			</button>
		</div>

	<!-- STEP 3: Masked ID, Selfie & Consent -->
	{:else if currentStep === 3}
		<div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-5">
			<h2 class="text-base font-bold text-citu-slate border-b pb-2">
				{translations[lang as 'ml' | 'en'].step3}
			</h2>

			<!-- DPDP Security Notice -->
			<div class="bg-blue-50 border border-blue-200 text-blue-900 rounded-xl p-3 text-xs flex items-start space-x-2.5">
				<span class="text-base">🛡️</span>
				<p>{translations[lang as 'ml' | 'en'].dpdpNotice}</p>
			</div>

			<!-- Live Selfie Widget -->
			<div class="border-2 border-dashed border-slate-300 rounded-xl p-4 text-center space-y-3 bg-slate-50">
				<div class="w-24 h-24 rounded-full mx-auto bg-slate-200 border-2 border-citu-red overflow-hidden flex items-center justify-center text-slate-400 font-bold">
					<span class="text-3xl">👤</span>
				</div>
				<div>
					<p class="text-xs font-bold text-slate-700">
						{translations[lang as 'ml' | 'en'].liveSelfie}
					</p>
					<p class="text-[11px] text-slate-500">
						{lang === 'ml' ? 'മുഖം വ്യക്തമായി കാണുന്ന രീതിയിൽ' : 'Clear face preview without helmet/sunglasses'}
					</p>
				</div>
				<button
					type="button"
					class="px-4 py-2 bg-slate-800 text-white rounded-lg text-xs font-semibold hover:bg-black touch-target"
				>
					{translations[lang as 'ml' | 'en'].takeSelfie}
				</button>
			</div>

			<!-- Masked ID -->
			<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
				<div class="space-y-1">
					<label for="id-doc-type" class="block text-xs font-bold text-slate-700">
						{translations[lang as 'ml' | 'en'].idDocType}
					</label>
					<select
						id="id-doc-type"
						bind:value={idDocType}
						class="w-full px-3 py-2.5 border border-slate-300 rounded-lg text-sm touch-target bg-white"
					>
						<option value="Aadhaar">{lang === 'ml' ? 'ആധാർ കാർഡ് (Aadhaar)' : 'Aadhaar Card'}</option>
						<option value="Driving Licence">{lang === 'ml' ? 'ഡ്രൈവിംഗ് ലൈസൻസ് (DL)' : 'Driving Licence'}</option>
						<option value="Voter ID">{lang === 'ml' ? 'തിരിച്ചറിയൽ കാർഡ് (Voter ID)' : 'Voter ID'}</option>
					</select>
				</div>

				<div class="space-y-1">
					<label for="id-last-4" class="block text-xs font-bold text-slate-700">
						{translations[lang as 'ml' | 'en'].idLast4}
					</label>
					<input
						id="id-last-4"
						type="text"
						bind:value={idLast4}
						placeholder="•••• 4821"
						maxlength="4"
						class="w-full px-3 py-2.5 border border-slate-300 rounded-lg text-sm font-mono tracking-widest touch-target"
					/>
				</div>
			</div>

			<!-- Consent Checkbox -->
			<div class="pt-3 border-t border-slate-200">
				<label class="flex items-start space-x-3 cursor-pointer">
					<input
						type="checkbox"
						bind:checked={consentGiven}
						class="mt-1 h-5 w-5 text-citu-red rounded border-slate-300 focus:ring-citu-red"
					/>
					<span class="text-xs text-slate-700 leading-relaxed font-medium">
						{translations[lang as 'ml' | 'en'].consentStatement}
					</span>
				</label>
			</div>

			<button
				onclick={handleCompleteRegistration}
				class="w-full bg-citu-red hover:bg-citu-red-dark text-white font-bold py-3.5 px-4 rounded-xl shadow-md transition touch-target flex items-center justify-center space-x-2"
			>
				<span>{translations[lang as 'ml' | 'en'].payAndJoin}</span>
				<span>✓</span>
			</button>
		</div>

	<!-- STEP 4: Digital Membership Card & WhatsApp Link -->
	{:else if currentStep === 4}
		<div class="space-y-6">
			<!-- Success Banner -->
			<div class="bg-emerald-600 text-white p-5 rounded-2xl shadow-md text-center space-y-1">
				<div class="text-2xl">🎉</div>
				<h2 class="text-base sm:text-lg font-bold">
					{translations[lang as 'ml' | 'en'].congratsComrade}
				</h2>
				<p class="text-xs text-emerald-100 font-mono tracking-wider">
					{translations[lang as 'ml' | 'en'].membershipNo}: <span class="bg-emerald-800/80 px-2 py-0.5 rounded font-bold text-white">{membershipNumber}</span>
				</p>
			</div>

			<!-- Digital Union Membership ID Card (Realistic Virtual Card) -->
			<div class="bg-gradient-to-br from-citu-red via-citu-red-dark to-slate-900 text-white rounded-2xl shadow-xl overflow-hidden border-2 border-yellow-400/50">
				<!-- Card Ribbon -->
				<div class="bg-black/25 px-4 py-2 flex items-center justify-between border-b border-white/10">
					<div class="flex items-center space-x-2">
						<span class="text-yellow-400 font-bold text-lg">★</span>
						<span class="text-[11px] font-bold tracking-wider uppercase text-yellow-300">
							CITU KERALA GIG WORKERS UNION
						</span>
					</div>
					<span class="text-[10px] bg-emerald-500 text-white px-2 py-0.5 rounded-full font-bold">
						ACTIVE
					</span>
				</div>

				<!-- Card Content -->
				<div class="p-5 flex flex-col sm:flex-row items-center sm:items-start space-y-4 sm:space-y-0 sm:space-x-4">
					<!-- Photo -->
					<div class="w-24 h-28 rounded-xl bg-slate-200 border-2 border-white/80 overflow-hidden flex-shrink-0 flex items-center justify-center text-slate-500 font-bold text-4xl shadow-md">
						👤
					</div>

					<!-- Details -->
					<div class="flex-1 space-y-1.5 text-center sm:text-left text-xs">
						<div class="text-base font-bold text-white">
							{fullName || 'Com. Rahul Krishnan'}
						</div>
						<div class="text-yellow-300 font-mono font-bold text-sm">
							ID: {membershipNumber}
						</div>
						<div class="text-slate-200 text-xs">
							{lang === 'ml' ? 'ജില്ല: എറണാകുളം (Ernakulam)' : 'District: Ernakulam Zone'}
						</div>
						<div class="text-slate-300 text-[11px]">
							{lang === 'ml' ? 'പ്ലാറ്റ്‌ഫോം:' : 'Platform:'} <span class="font-bold text-white">{primaryPlatform}</span>
						</div>
						<div class="text-slate-300 text-[11px]">
							{lang === 'ml' ? 'കാലാവധി: ഏപ്രിൽ 2027 വരെ' : 'Valid Thru: April 2027'}
						</div>
					</div>

					<!-- QR Code -->
					<div class="w-20 h-20 bg-white p-1 rounded-xl shadow-inner flex flex-col items-center justify-center flex-shrink-0">
						<div class="text-citu-slate font-mono text-[9px] font-bold">QR VERIFY</div>
						<div class="text-2xl text-slate-900">▦</div>
						<div class="text-[8px] text-slate-500 font-mono">TOKEN</div>
					</div>
				</div>
			</div>

			<!-- Card Action Buttons -->
			<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
				<button
					type="button"
					class="w-full bg-citu-red hover:bg-citu-red-dark text-white font-bold py-3 px-4 rounded-xl shadow transition touch-target text-xs flex items-center justify-center space-x-2"
				>
					<span>📥</span>
					<span>{translations[lang as 'ml' | 'en'].downloadCardPdf}</span>
				</button>
				<button
					type="button"
					class="w-full bg-white hover:bg-slate-50 text-slate-800 font-bold py-3 px-4 rounded-xl border border-slate-300 shadow-sm transition touch-target text-xs flex items-center justify-center space-x-2"
				>
					<span>🧾</span>
					<span>{translations[lang as 'ml' | 'en'].viewReceipt} (₹160)</span>
				</button>
			</div>

			<!-- District WhatsApp Group Link -->
			<div class="bg-emerald-50 border border-emerald-200 rounded-2xl p-5 space-y-3">
				<div class="flex items-center space-x-3">
					<div class="w-10 h-10 rounded-full bg-emerald-600 text-white flex items-center justify-center text-xl font-bold">
						💬
					</div>
					<div>
						<h3 class="text-sm font-bold text-emerald-900">
							{translations[lang as 'ml' | 'en'].joinWhatsApp}
						</h3>
						<p class="text-xs text-emerald-700">
							{lang === 'ml'
								? 'എറണാകുളം ജില്ലാ വാട്സ്ആപ്പ് ഗ്രൂപ്പിൽ ചേരുക. തത്സമയ യൂണിയൻ അറിയിപ്പുകൾ ലഭിക്കും.'
								: 'Join the Ernakulam District WhatsApp group for union alerts and local support.'}
						</p>
					</div>
				</div>
				<a
					href="https://chat.whatsapp.com/mock-citu-ekm"
					target="_blank"
					rel="noreferrer"
					class="block w-full text-center bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-3 px-4 rounded-xl shadow transition text-xs touch-target"
				>
					{translations[lang as 'ml' | 'en'].joinWhatsApp} →
				</a>
			</div>

			<!-- Grievance & Legal Aid Contacts -->
			<div class="bg-white border border-slate-200 rounded-2xl p-5 space-y-3 text-xs">
				<h3 class="font-bold text-citu-slate border-b pb-2 flex items-center space-x-2">
					<span>⚖️</span>
					<span>{translations[lang as 'ml' | 'en'].grievanceHelp}</span>
				</h3>
				<div class="space-y-1.5 text-slate-600">
					<p><span class="font-semibold text-slate-800">{lang === 'ml' ? 'ജില്ലാ കൺവീനർ:' : 'District Convenor:'}</span> P. V. Suresh (+91 94471 20491)</p>
					<p><span class="font-semibold text-slate-800">{lang === 'ml' ? 'നിയമോപദേശകൻ:' : 'Legal Advisor:'}</span> Adv. K. Madhavan (+91 94472 88102)</p>
					<p><span class="font-semibold text-slate-800">{lang === 'ml' ? 'യൂണിയൻ ഓഫീസ്:' : 'Union Office:'}</span> CITU Bhavan, High Court Road, Ernakulam</p>
				</div>
			</div>
		</div>
	{/if}
</div>
