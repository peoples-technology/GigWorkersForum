<script lang="ts">
	import { onMount } from 'svelte';

	let lang = $state<'ml' | 'en'>('ml');
	let activeStep = $state(1);
	let saveStatus = $state('Draft saved locally');

	// Step 1: Mobile & OTP
	let mobile = $state('');
	let otpCode = $state('');
	let otpSent = $state(false);
	let timer = $state(45);
	let timerInterval: any = null;
	let phoneError = $state('');

	// Step 2: Personal
	let fullName = $state('');
	let dob = $state('');
	let age = $state<number | null>(null);
	let gender = $state('');
	let motherTongue = $state('Malayalam');
	let email = $state('');
	let currentAddress = $state('');
	let sameWhatsapp = $state(true);
	let whatsappNumber = $state('');

	// Step 3: Work & Identity
	let workingDistrict = $state('');
	let primarySector = $state('');
	let primaryPlatform = $state('');
	let customPlatform = $state('');
	let workingMode = $state('Full Time');
	let vehicleNumber = $state('');
	let licenceNumber = $state('');
	let idDocType = $state('Aadhaar');
	let idLastDigits = $state('');

	// Step 4: Selfie & Consent
	let cameraActive = $state(false);
	let capturedPhoto = $state('');
	let videoElement: HTMLVideoElement | null = $state(null);
	let videoStream: MediaStream | null = null;
	let consentAgreed = $state(false);
	let submitting = $state(false);

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

	const sectorPlatformMap: Record<string, string[]> = {
		'Delivery': ['Zomato', 'Swiggy', 'Instamart', 'BigBasket', 'Blinkit', 'Flipkart Minutes', 'Porter', 'Shadowfax', 'Ecom Express', 'Delhivery', 'Other'],
		'Ride Hailing': ['Uber', 'Ola', 'Rapido', 'Kerala Savari', 'Yatri', 'Other'],
		'On-Demand': ['Urban Company', 'Free Hour', 'Hiird', 'Other'],
		'Other': ['Other']
	};

	let availablePlatforms = $derived(primarySector ? sectorPlatformMap[primarySector] || [] : []);

	function calculateAge(dobString: string) {
		if (!dobString) {
			age = null;
			return;
		}
		const birthDate = new Date(dobString);
		const diff = Date.now() - birthDate.getTime();
		const ageDate = new Date(diff);
		age = Math.abs(ageDate.getUTCFullYear() - 1970);
	}

	function sendOtp() {
		phoneError = '';
		if (!/^[6-9]\d{9}$/.test(mobile.trim())) {
			phoneError = lang === 'ml' 
				? 'സാധുവായ 10 അക്ക മൊബൈൽ നമ്പർ നൽകുക' 
				: 'Please enter a valid 10-digit mobile number';
			return;
		}

		otpSent = true;
		timer = 45;
		clearInterval(timerInterval);
		timerInterval = setInterval(() => {
			if (timer > 0) {
				timer--;
			} else {
				clearInterval(timerInterval);
			}
		}, 1000);
	}

	function verifyOtp() {
		if (!otpCode || otpCode.trim().length !== 6) {
			alert(lang === 'ml' ? 'ദയവായി 6 അക്ക OTP കോഡ് നൽകുക.' : 'Please enter a valid 6-digit OTP code.');
			return;
		}
		triggerAutoSave();
		activeStep = 2;
		window.scrollTo({ top: 0, behavior: 'smooth' });
	}

	function validateStep2() {
		if (!fullName.trim() || !dob || !gender || !currentAddress.trim()) {
			alert(lang === 'ml' ? 'ദയവായി എല്ലാ നിർബന്ധിത വിവരങ്ങളും പൂരിപ്പിക്കുക.' : 'Please fill all required personal fields.');
			return;
		}
		if (age !== null && age < 18) {
			alert(lang === 'ml' ? 'യൂണിയൻ അംഗത്വത്തിന് കുറഞ്ഞത് 18 വയസ്സ് പൂർത്തിയാകണം.' : 'Workers must be at least 18 years old to join the union.');
			return;
		}
		triggerAutoSave();
		activeStep = 3;
		window.scrollTo({ top: 0, behavior: 'smooth' });
	}

	function validateStep3() {
		if (!workingDistrict || !primarySector || !primaryPlatform || !idLastDigits.trim()) {
			alert(lang === 'ml' ? 'ദയവായി തൊഴിൽ, തിരിച്ചറിയൽ വിവരങ്ങൾ പൂർണ്ണമായി നൽകുക.' : 'Please fill all required work and identity fields.');
			return;
		}
		if (!/^\d{4}$/.test(idLastDigits.trim())) {
			alert(lang === 'ml' ? 'തിരിച്ചറിയൽ കാർഡിന്റെ അവസാന 4 അക്കങ്ങൾ മാത്രം നൽകുക.' : 'Please enter exactly 4 digits for your government ID proof.');
			return;
		}
		triggerAutoSave();
		activeStep = 4;
		window.scrollTo({ top: 0, behavior: 'smooth' });
	}

	async function startCamera() {
		try {
			videoStream = await navigator.mediaDevices.getUserMedia({
				video: { facingMode: 'user', width: { ideal: 480 }, height: { ideal: 480 } },
				audio: false
			});
			cameraActive = true;
			if (videoElement) {
				videoElement.srcObject = videoStream;
			}
		} catch (err) {
			alert(lang === 'ml' 
				? 'ക്യാമറ ആക്സസ് ചെയ്യാൻ സാധിച്ചില്ല. ബ്രൗസർ അനുമതി നൽകുക അല്ലെങ്കിൽ ഫോട്ടോ അപ്‌ലോഡ് ചെയ്യുക.' 
				: 'Camera access denied or unavailable. Please grant camera permission.');
		}
	}

	function capturePhoto() {
		if (!videoElement) return;
		const canvas = document.createElement('canvas');
		canvas.width = 400;
		canvas.height = 400;
		const ctx = canvas.getContext('2d');
		if (ctx) {
			ctx.drawImage(videoElement, 0, 0, 400, 400);
			capturedPhoto = canvas.toDataURL('image/jpeg', 0.85);
		}
		stopCamera();
	}

	function stopCamera() {
		if (videoStream) {
			videoStream.getTracks().forEach(track => track.stop());
			videoStream = null;
		}
		cameraActive = false;
	}

	function retakePhoto() {
		capturedPhoto = '';
		startCamera();
	}

	function handleFileUpload(e: Event) {
		const target = e.target as HTMLInputElement;
		if (target.files && target.files[0]) {
			const reader = new FileReader();
			reader.onload = (event) => {
				capturedPhoto = event.target?.result as string;
			};
			reader.readAsDataURL(target.files[0]);
		}
	}

	function triggerAutoSave() {
		const draft = {
			mobile,
			fullName,
			dob,
			gender,
			motherTongue,
			email,
			currentAddress,
			workingDistrict,
			primarySector,
			primaryPlatform,
			customPlatform,
			workingMode,
			vehicleNumber,
			licenceNumber,
			idDocType,
			idLastDigits
		};
		try {
			localStorage.setItem('ksgpwu_reg_draft', JSON.stringify(draft));
			saveStatus = lang === 'ml' ? 'ഡ്രാഫ്റ്റ് സേവ് ചെയ്തു' : 'Draft auto-saved';
			setTimeout(() => {
				saveStatus = lang === 'ml' ? 'ഡ്രാഫ്റ്റ് ലോക്കൽ സേവിലാണ്' : 'Draft saved locally';
			}, 2500);
		} catch (e) {
			console.error(e);
		}
	}

	function proceedToPayment() {
		if (!capturedPhoto) {
			alert(lang === 'ml' ? 'ദയവായി നിങ്ങളുടെ ഫോട്ടോ എടുക്കുക അല്ലെങ്കിൽ അപ്‌ലോഡ് ചെയ്യുക.' : 'Please capture or upload your photo before continuing.');
			return;
		}
		if (!consentAgreed) {
			alert(lang === 'ml' ? 'ദയവായി യൂണിയൻ സത്യപ്രസ്താവനയും സ്വകാര്യതാ സമ്മതവും അംഗീകരിക്കുക.' : 'Please check the union declaration and privacy consent checkbox.');
			return;
		}

		submitting = true;

		const payload = {
			mobile,
			fullName,
			dob,
			gender,
			motherTongue,
			email,
			currentAddress,
			workingDistrict,
			primarySector,
			primaryPlatform: primaryPlatform === 'Other' ? customPlatform : primaryPlatform,
			workingMode,
			vehicleNumber,
			licenceNumber,
			idDocType,
			idLastDigits,
			photo: capturedPhoto,
			amount: 100,
			timestamp: new Date().toISOString()
		};

		// Save payload for Screen 3 (Checkout)
		sessionStorage.setItem('pendingRegistration', JSON.stringify(payload));

		// Navigate to checkout
		window.location.href = `/checkout?district=${workingDistrict}&mobile=${mobile}&name=${encodeURIComponent(fullName)}`;
	}

	onMount(() => {
		try {
			const saved = localStorage.getItem('ksgpwu_reg_draft');
			if (saved) {
				const d = JSON.parse(saved);
				if (d.mobile) mobile = d.mobile;
				if (d.fullName) fullName = d.fullName;
				if (d.dob) {
					dob = d.dob;
					calculateAge(d.dob);
				}
				if (d.gender) gender = d.gender;
				if (d.motherTongue) motherTongue = d.motherTongue;
				if (d.email) email = d.email;
				if (d.currentAddress) currentAddress = d.currentAddress;
				if (d.workingDistrict) workingDistrict = d.workingDistrict;
				if (d.primarySector) primarySector = d.primarySector;
				if (d.primaryPlatform) primaryPlatform = d.primaryPlatform;
				if (d.customPlatform) customPlatform = d.customPlatform;
				if (d.workingMode) workingMode = d.workingMode;
				if (d.vehicleNumber) vehicleNumber = d.vehicleNumber;
				if (d.licenceNumber) licenceNumber = d.licenceNumber;
				if (d.idDocType) idDocType = d.idDocType;
				if (d.idLastDigits) idLastDigits = d.idLastDigits;
			}
		} catch (e) {
			console.error('Failed to restore draft', e);
		}

		return () => {
			stopCamera();
			clearInterval(timerInterval);
		};
	});
</script>

<svelte:head>
	<title>{lang === 'ml' ? 'അംഗത്വ രജിസ്ട്രേഷൻ | GigWorkers.Online' : 'Member Registration | GigWorkers.Online'}</title>
</svelte:head>

<!-- Header -->
<header class="bg-white/95 backdrop-blur-md border-b border-slate-200/80 sticky top-0 z-40 shadow-xs">
	<div class="max-w-5xl mx-auto px-3 sm:px-6 h-16 flex items-center justify-between gap-2">
		<!-- Union Logo & Identity -->
		<a href="/" class="flex items-center space-x-2 sm:space-x-3 group min-w-0 flex-shrink">
			<div class="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-gradient-to-br from-red-600 via-primary to-red-900 text-white flex items-center justify-center font-bold text-base sm:text-lg shadow-sm group-hover:scale-105 transition-transform flex-shrink-0">
				★
			</div>
			<div class="min-w-0">
				<span class="font-extrabold text-sm sm:text-base tracking-tight text-slate-900 block group-hover:text-primary transition truncate">GigWorkers.Online</span>
				<span class="text-[10px] sm:text-xs text-slate-500 font-medium block truncate">
					{lang === 'ml' ? 'കേരള ഗിഗ് & പ്ലാറ്റ്‌ഫോം വർക്കേഴ്സ് യൂണിയൻ' : 'Kerala Gig & Platform Workers Union'}
				</span>
			</div>
		</a>

		<!-- Language Switcher & Home link -->
		<div class="flex items-center space-x-1.5 sm:space-x-3 flex-shrink-0">
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

			<a href="/" class="hidden sm:inline-flex text-xs font-bold text-slate-600 hover:text-primary transition items-center gap-1">
				<span class="material-symbols-outlined text-[16px]">arrow_back</span>
				<span>{lang === 'ml' ? 'ഹോം' : 'Home'}</span>
			</a>
		</div>
	</div>
</header>

<!-- Main Form Container with Atmospheric Mesh Background -->
<div class="hero-gradient-mesh min-h-screen py-8">
<main class="flex-grow max-w-4xl w-full mx-auto px-4 sm:px-6">
	<!-- Title & Autosave Pill -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-slate-200 mb-8 gap-4">
		<div>
			<div class="inline-flex items-center gap-1.5 text-xs uppercase font-extrabold tracking-wider text-primary mb-1">
				<span class="w-2 h-2 rounded-full bg-primary"></span>
				<span>{lang === 'ml' ? 'യൂണിയൻ അംഗത്വ രജിസ്ട്രേഷൻ' : 'Union Membership Enrollment'}</span>
			</div>
			<h1 class="text-2xl sm:text-3xl font-black text-slate-900">
				{lang === 'ml' ? 'അംഗത്വ രജിസ്ട്രേഷൻ ഫോം' : 'Member Registration Form'}
			</h1>
			<p class="text-xs sm:text-sm text-slate-500 mt-1 font-medium">
				{lang === 'ml' ? 'ഏകദേശം 3 മിനിറ്റ് മാത്രം. വിവരങ്ങൾ സ്വയമേവ സേവ് ചെയ്യപ്പെടുന്നു.' : 'Takes ~3 minutes. Your progress saves automatically.'}
			</p>
		</div>

		<!-- Autosave indicator -->
		<div class="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white border border-slate-200 text-xs text-slate-600 self-start sm:self-auto shadow-sm">
			<span class="relative flex h-2 w-2">
				<span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
				<span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
			</span>
			<span class="font-semibold">{saveStatus}</span>
		</div>
	</div>

	<!-- Step Progress Tracker -->
	<div class="mb-10">
		<div class="flex items-center justify-between relative">
			<div class="absolute left-0 top-1/2 -translate-y-1/2 h-1 w-full bg-slate-200 rounded-full -z-0"></div>

			<!-- Step 1 Indicator -->
			<div class="relative z-10 flex flex-col items-center">
				<div class={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm border-2 transition shadow-md ${activeStep === 1 ? 'bg-primary text-white border-primary ring-4 ring-red-100' : activeStep > 1 ? 'bg-emerald-600 text-white border-emerald-600' : 'bg-white text-slate-400 border-slate-300'}`}>
					{#if activeStep > 1}
						<span class="material-symbols-outlined text-[20px]">check</span>
					{:else}
						1
					{/if}
				</div>
				<span class="text-xs font-bold mt-2 text-slate-800 hidden sm:block">
					{lang === 'ml' ? 'മൊബൈൽ OTP' : 'Phone OTP'}
				</span>
			</div>

			<!-- Step 2 Indicator -->
			<div class="relative z-10 flex flex-col items-center">
				<div class={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm border-2 transition shadow-md ${activeStep === 2 ? 'bg-primary text-white border-primary ring-4 ring-red-100' : activeStep > 2 ? 'bg-emerald-600 text-white border-emerald-600' : 'bg-white text-slate-400 border-slate-300'}`}>
					{#if activeStep > 2}
						<span class="material-symbols-outlined text-[20px]">check</span>
					{:else}
						2
					{/if}
				</div>
				<span class="text-xs font-bold mt-2 text-slate-600 hidden sm:block">
					{lang === 'ml' ? 'വ്യക്തിവിവരങ്ങൾ' : 'Personal Info'}
				</span>
			</div>

			<!-- Step 3 Indicator -->
			<div class="relative z-10 flex flex-col items-center">
				<div class={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm border-2 transition shadow-md ${activeStep === 3 ? 'bg-primary text-white border-primary ring-4 ring-red-100' : activeStep > 3 ? 'bg-emerald-600 text-white border-emerald-600' : 'bg-white text-slate-400 border-slate-300'}`}>
					{#if activeStep > 3}
						<span class="material-symbols-outlined text-[20px]">check</span>
					{:else}
						3
					{/if}
				</div>
				<span class="text-xs font-bold mt-2 text-slate-600 hidden sm:block">
					{lang === 'ml' ? 'തൊഴിൽ & രേഖ' : 'Work & ID'}
				</span>
			</div>

			<!-- Step 4 Indicator -->
			<div class="relative z-10 flex flex-col items-center">
				<div class={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm border-2 transition shadow-md ${activeStep === 4 ? 'bg-primary text-white border-primary ring-4 ring-red-100' : 'bg-white text-slate-400 border-slate-300'}`}>
					4
				</div>
				<span class="text-xs font-bold mt-2 text-slate-600 hidden sm:block">
					{lang === 'ml' ? 'ഫോട്ടോ & സമ്മതം' : 'Selfie & Consent'}
				</span>
			</div>
		</div>
	</div>

	<!-- Form Card -->
	<div class="card-gloss rounded-3xl p-6 sm:p-10 shadow-xl transition">
		<!-- STEP 1: Mobile & OTP -->
		{#if activeStep === 1}
			<section class="space-y-6">
				<div>
					<h2 class="text-xl font-bold text-on-surface flex items-center gap-2">
						<span class="material-symbols-outlined text-primary">smartphone</span>
						<span>{lang === 'ml' ? 'മൊബൈൽ നമ്പർ സ്ഥിരീകരിക്കുക' : 'Mobile Number Verification'}</span>
					</h2>
					<p class="text-sm text-secondary mt-1">
						{lang === 'ml' 
							? 'നിങ്ങളുടെ മൊബൈൽ നമ്പർ OTP വഴി പരിശോധിക്കും. ഇതായിരിക്കും യൂണിയൻ ലോഗിൻ ഐഡി.' 
							: 'We verify your mobile number via OTP. This number will become your unique login identifier.'}
					</p>
				</div>

				<div class="space-y-4 max-w-md">
					<div>
						<label for="mobile-number-input" class="block text-xs font-bold uppercase tracking-wider text-secondary mb-1.5">
							{lang === 'ml' ? 'മൊബൈൽ നമ്പർ' : 'Mobile Number'} <span class="text-primary">*</span>
						</label>
						<div class="flex rounded-lg shadow-xs border border-surface-variant focus-within:ring-2 focus-within:ring-primary focus-within:border-primary overflow-hidden">
							<span class="inline-flex items-center px-3.5 bg-surface-container text-secondary text-sm font-semibold border-r border-surface-variant">
								+91
							</span>
							<input 
								id="mobile-number-input"
								type="tel" 
								bind:value={mobile} 
								maxlength="10" 
								placeholder="9876543210" 
								class="block w-full px-3 py-2.5 text-on-surface placeholder:text-secondary/50 focus:outline-none text-sm font-medium bg-transparent"
							/>
						</div>
						{#if phoneError}
							<p class="text-xs text-primary mt-1">{phoneError}</p>
						{/if}
					</div>

					<!-- OTP Container -->
					{#if otpSent}
						<div class="space-y-3 pt-2">
							<label for="otp-code-input" class="block text-xs font-bold uppercase tracking-wider text-secondary">
								{lang === 'ml' ? '6 അക്ക OTP നൽകുക' : 'Enter 6-Digit OTP'} <span class="text-primary">*</span>
							</label>
							<div class="flex gap-2">
								<input 
									id="otp-code-input"
									type="text" 
									bind:value={otpCode} 
									maxlength="6" 
									placeholder="123456" 
									class="w-full tracking-widest text-center text-lg font-bold px-3 py-2 rounded-lg border border-surface-variant focus:ring-2 focus:ring-primary focus:border-primary focus:outline-none bg-surface-container-low"
								/>
							</div>
							<div class="flex items-center justify-between text-xs text-secondary">
								<span>{lang === 'ml' ? 'കോഡ് വീണ്ടും അയക്കുക' : 'Resend in'} <strong>00:{timer < 10 ? '0' : ''}{timer}</strong></span>
								<button 
									type="button" 
									onclick={sendOtp} 
									disabled={timer > 0} 
									class="text-primary font-semibold hover:underline disabled:opacity-40"
								>
									{lang === 'ml' ? 'വീണ്ടും അയക്കുക' : 'Resend OTP'}
								</button>
							</div>

							<!-- Helper hint for testing -->
							<div class="p-2.5 rounded bg-surface-container text-xs text-secondary flex items-center gap-1.5">
								<span class="material-symbols-outlined text-[16px] text-tertiary">info</span>
								<span>Test OTP: <strong>123456</strong> (or any 6 digits)</span>
							</div>
						</div>
					{/if}

					<div class="pt-2">
						{#if !otpSent}
							<button 
								type="button" 
								onclick={sendOtp}
								class="w-full py-3.5 px-4 crimson-gradient-btn text-white font-bold rounded-xl shadow-md text-sm transition flex items-center justify-center gap-2"
							>
								<span class="material-symbols-outlined text-[18px]">send</span>
								<span>{lang === 'ml' ? 'OTP അയക്കുക' : 'Send OTP'}</span>
							</button>
						{:else}
							<button 
								type="button" 
								onclick={verifyOtp}
								class="w-full py-3.5 px-4 crimson-gradient-btn text-white font-bold rounded-xl shadow-md text-sm transition flex items-center justify-center gap-2"
							>
								<span class="material-symbols-outlined text-[18px]">verified</span>
								<span>{lang === 'ml' ? 'സ്ഥിരീകരിച്ച് തുടരുക' : 'Verify OTP & Continue'}</span>
							</button>
						{/if}
					</div>
				</div>
			</section>
		{/if}

		<!-- STEP 2: Personal Details -->
		{#if activeStep === 2}
			<section class="space-y-6">
				<div>
					<h2 class="text-xl font-bold text-on-surface flex items-center gap-2">
						<span class="material-symbols-outlined text-primary">person</span>
						<span>{lang === 'ml' ? 'വ്യക്തിഗത വിവരങ്ങൾ' : 'Personal Information'}</span>
					</h2>
					<p class="text-sm text-secondary mt-1">
						{lang === 'ml' 
							? 'അംഗത്വ കാർഡിൽ പ്രിന്റ് ചെയ്യുന്നതിനുള്ള ശരിയായ വിവരങ്ങൾ നൽകുക.' 
							: 'Provide your personal details accurately as they will appear on your union membership card.'}
					</p>
				</div>

				<div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
					<!-- Full Name -->
					<div class="sm:col-span-2">
						<label for="full-name-input" class="block text-xs font-bold uppercase tracking-wider text-secondary mb-1">
							{lang === 'ml' ? 'പൂർണ്ണമായ പേര് (രേഖയിലുള്ളതുപോലെ)' : 'Full Name (As in ID)'} <span class="text-primary">*</span>
						</label>
						<input 
							id="full-name-input"
							type="text" 
							bind:value={fullName}
							oninput={triggerAutoSave}
							placeholder="e.g. Sreekumar P" 
							required
							class="w-full px-3.5 py-2.5 rounded-lg border border-surface-variant text-sm focus:ring-2 focus:ring-primary focus:border-primary focus:outline-none bg-surface-container-lowest"
						/>
					</div>

					<!-- DOB -->
					<div>
						<label for="dob-input" class="block text-xs font-bold uppercase tracking-wider text-secondary mb-1">
							{lang === 'ml' ? 'ജനന തീയതി' : 'Date of Birth'} <span class="text-primary">*</span>
						</label>
						<input 
							id="dob-input"
							type="date" 
							bind:value={dob}
							onchange={() => { calculateAge(dob); triggerAutoSave(); }}
							required
							class="w-full px-3.5 py-2.5 rounded-lg border border-surface-variant text-sm focus:ring-2 focus:ring-primary focus:border-primary focus:outline-none bg-surface-container-lowest"
						/>
						{#if age !== null}
							<div class="mt-1 text-xs font-medium">
								{#if age < 18}
									<span class="text-primary font-semibold">Underage: {age} years (Min 18 required)</span>
								{:else}
									<span class="text-green-700 font-semibold">Age: {age} years (Eligible)</span>
								{/if}
							</div>
						{:else}
							<div class="mt-1 text-xs text-secondary font-medium">Min age 18 years</div>
						{/if}
					</div>

					<!-- Gender -->
					<div>
						<label for="gender-select" class="block text-xs font-bold uppercase tracking-wider text-secondary mb-1">
							{lang === 'ml' ? 'ലിംഗം' : 'Gender'} <span class="text-primary">*</span>
						</label>
						<select 
							id="gender-select"
							bind:value={gender}
							onchange={triggerAutoSave}
							required 
							class="w-full px-3.5 py-2.5 rounded-lg border border-surface-variant text-sm focus:ring-2 focus:ring-primary focus:border-primary focus:outline-none bg-surface-container-lowest"
						>
							<option value="" disabled selected>{lang === 'ml' ? 'തിരഞ്ഞെടുക്കുക' : 'Select Gender'}</option>
							<option value="Male">{lang === 'ml' ? 'പുരുഷൻ (Male)' : 'Male'}</option>
							<option value="Female">{lang === 'ml' ? 'സ്ത്രീ (Female)' : 'Female'}</option>
							<option value="Others">{lang === 'ml' ? 'മറ്റുള്ളവ (Others)' : 'Others'}</option>
						</select>
					</div>

					<!-- Mother Tongue -->
					<div>
						<label for="mother-tongue-input" class="block text-xs font-bold uppercase tracking-wider text-secondary mb-1">
							{lang === 'ml' ? 'മാതൃഭാഷ' : 'Mother Tongue'}
						</label>
						<input 
							id="mother-tongue-input"
							type="text" 
							bind:value={motherTongue} 
							oninput={triggerAutoSave}
							class="w-full px-3.5 py-2.5 rounded-lg border border-surface-variant text-sm focus:ring-2 focus:ring-primary focus:border-primary focus:outline-none bg-surface-container-lowest"
						/>
					</div>

					<!-- Email -->
					<div>
						<label for="email-input" class="block text-xs font-bold uppercase tracking-wider text-secondary mb-1">
							{lang === 'ml' ? 'ഇമെയിൽ വിലാസം (നിർബന്ധമില്ല)' : 'Email Address (Optional)'}
						</label>
						<input 
							id="email-input"
							type="email" 
							bind:value={email} 
							oninput={triggerAutoSave}
							placeholder="name@example.com" 
							class="w-full px-3.5 py-2.5 rounded-lg border border-surface-variant text-sm focus:ring-2 focus:ring-primary focus:border-primary focus:outline-none bg-surface-container-lowest"
						/>
					</div>

					<!-- Address -->
					<div class="sm:col-span-2">
						<label for="current-address-input" class="block text-xs font-bold uppercase tracking-wider text-secondary mb-1">
							{lang === 'ml' ? 'നിലവിലെ താമസ വിലാസം' : 'Current Residential Address'} <span class="text-primary">*</span>
						</label>
						<textarea 
							id="current-address-input"
							bind:value={currentAddress} 
							oninput={triggerAutoSave}
							rows="2" 
							required 
							placeholder="House / Room No, Street, Town, PIN" 
							class="w-full px-3.5 py-2.5 rounded-lg border border-surface-variant text-sm focus:ring-2 focus:ring-primary focus:border-primary focus:outline-none bg-surface-container-lowest"
						></textarea>
					</div>

					<!-- WhatsApp Option -->
					<div class="sm:col-span-2 flex items-center gap-2 pt-1">
						<input 
							type="checkbox" 
							id="sameWhatsapp" 
							bind:checked={sameWhatsapp} 
							class="w-4 h-4 text-primary rounded border-surface-variant focus:ring-primary"
						/>
						<label for="sameWhatsapp" class="text-xs font-medium text-secondary">
							{lang === 'ml' ? 'വാട്‌സ്ആപ്പ് നമ്പർ മൊബൈൽ നമ്പറിന് തുല്യമാണ്' : 'WhatsApp number is the same as my registered mobile number'}
						</label>
					</div>
				</div>

				<div class="pt-4 flex justify-between border-t border-slate-200">
					<button 
						type="button" 
						onclick={() => activeStep = 1} 
						class="px-5 py-2.5 border border-slate-300 text-slate-700 font-semibold rounded-xl hover:bg-slate-50 text-sm shadow-xs"
					>
						{lang === 'ml' ? 'പിന്നോട്ട്' : 'Back'}
					</button>
					<button 
						type="button" 
						onclick={validateStep2} 
						class="px-7 py-2.5 crimson-gradient-btn text-white font-bold rounded-xl text-sm shadow-md"
					>
						{lang === 'ml' ? 'തുടരുക' : 'Continue'}
					</button>
				</div>
			</section>
		{/if}

		<!-- STEP 3: Work, Sector & Identity -->
		{#if activeStep === 3}
			<section class="space-y-6">
				<div>
					<h2 class="text-xl font-bold text-on-surface flex items-center gap-2">
						<span class="material-symbols-outlined text-primary">work</span>
						<span>{lang === 'ml' ? 'തൊഴിൽ മേഖല & തിരിച്ചറിയൽ രേഖ' : 'Work, Sector & Identity'}</span>
					</h2>
					<p class="text-sm text-secondary mt-1">
						{lang === 'ml' 
							? 'നിങ്ങൾ ജോലി ചെയ്യുന്ന ജില്ല യൂണിയൻ ഘടകത്തെയും വാട്‌സ്ആപ്പ് ഹെൽപ്പ്‌ഡെസ്കിനെയും നിശ്ചയിക്കുന്നു.' 
							: 'Your working district decides your union district unit and WhatsApp group.'}
					</p>
				</div>

				<div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
					<!-- Working District -->
					<div class="sm:col-span-2">
						<label for="working-district-select" class="block text-xs font-bold uppercase tracking-wider text-secondary mb-1">
							{lang === 'ml' ? 'ജോലി ചെയ്യുന്ന ജില്ല (14 ജില്ലകൾ)' : 'Working District (14 Districts of Kerala)'} <span class="text-primary">*</span>
						</label>
						<select 
							id="working-district-select"
							bind:value={workingDistrict} 
							onchange={triggerAutoSave}
							required 
							class="w-full px-3.5 py-2.5 rounded-lg border border-surface-variant text-sm focus:ring-2 focus:ring-primary focus:border-primary focus:outline-none bg-surface-container-lowest"
						>
							<option value="" disabled selected>{lang === 'ml' ? 'ജില്ല തിരഞ്ഞെടുക്കുക' : 'Select District'}</option>
							{#each districts as dist}
								<option value={dist.code}>
									{dist.en} ({dist.ml}) [{dist.code}]
								</option>
							{/each}
						</select>
					</div>

					<!-- Sector -->
					<div>
						<label for="primary-sector-select" class="block text-xs font-bold uppercase tracking-wider text-secondary mb-1">
							{lang === 'ml' ? 'പ്രധാന തൊഴിൽ മേഖല' : 'Primary Sector'} <span class="text-primary">*</span>
						</label>
						<select 
							id="primary-sector-select"
							bind:value={primarySector} 
							onchange={() => { primaryPlatform = ''; triggerAutoSave(); }}
							required 
							class="w-full px-3.5 py-2.5 rounded-lg border border-surface-variant text-sm focus:ring-2 focus:ring-primary focus:border-primary focus:outline-none bg-surface-container-lowest"
						>
							<option value="" disabled selected>{lang === 'ml' ? 'മേഖല തിരഞ്ഞെടുക്കുക' : 'Select Sector'}</option>
							<option value="Delivery">Delivery & Logistics (ഭക്ഷണ/പാഴ്സൽ വിതരണം)</option>
							<option value="Ride Hailing">Ride Hailing (ഓട്ടോ/ടാക്സി/ബൈക്ക്)</option>
							<option value="On-Demand">On-Demand Services (വീട്ടുസേവനങ്ങൾ)</option>
							<option value="Other">Other Sector (മറ്റു മേഖലകൾ)</option>
						</select>
					</div>

					<!-- Platform -->
					<div>
						<label for="primary-platform-select" class="block text-xs font-bold uppercase tracking-wider text-secondary mb-1">
							{lang === 'ml' ? 'പ്രവർത്തിക്കുന്ന പ്ലാറ്റ്‌ഫോം' : 'Primary Platform / Company'} <span class="text-primary">*</span>
						</label>
						<select 
							id="primary-platform-select"
							bind:value={primaryPlatform} 
							onchange={triggerAutoSave}
							required 
							disabled={!primarySector}
							class="w-full px-3.5 py-2.5 rounded-lg border border-surface-variant text-sm focus:ring-2 focus:ring-primary focus:border-primary focus:outline-none bg-surface-container-lowest disabled:opacity-50"
						>
							<option value="" disabled selected>{primarySector ? (lang === 'ml' ? 'കമ്പനി തിരഞ്ഞെടുക്കുക' : 'Select Platform') : (lang === 'ml' ? 'ആദ്യം മേഖല തിരഞ്ഞെടുക്കുക' : 'Select Sector First')}</option>
							{#each availablePlatforms as p}
								<option value={p}>{p}</option>
							{/each}
						</select>

						{#if primaryPlatform === 'Other'}
							<input 
								type="text" 
								bind:value={customPlatform} 
								oninput={triggerAutoSave}
								placeholder="Type platform name" 
								class="w-full mt-2 px-3.5 py-2 rounded-lg border border-surface-variant text-sm focus:ring-2 focus:ring-primary focus:border-primary bg-surface-container-lowest"
							/>
						{/if}
					</div>

					<!-- Working Mode -->
					<div class="sm:col-span-2">
						<span class="block text-xs font-bold uppercase tracking-wider text-secondary mb-1">
							{lang === 'ml' ? 'ജോലി സമയം' : 'Working Mode'} <span class="text-primary">*</span>
						</span>
						<div class="grid grid-cols-2 gap-4">
							<label class={`flex items-center p-3 rounded-lg border cursor-pointer transition ${workingMode === 'Full Time' ? 'border-primary bg-primary-fixed/40' : 'border-surface-variant hover:bg-surface-container'}`}>
								<input type="radio" bind:group={workingMode} value="Full Time" class="w-4 h-4 text-primary" />
								<span class="ml-2 text-xs font-semibold text-on-surface">Full Time / പൂർണ്ണ സമയം</span>
							</label>
							<label class={`flex items-center p-3 rounded-lg border cursor-pointer transition ${workingMode === 'Part Time' ? 'border-primary bg-primary-fixed/40' : 'border-surface-variant hover:bg-surface-container'}`}>
								<input type="radio" bind:group={workingMode} value="Part Time" class="w-4 h-4 text-primary" />
								<span class="ml-2 text-xs font-semibold text-on-surface">Part Time / ഭാഗിക സമയം</span>
							</label>
						</div>
					</div>

					<!-- Vehicle Details -->
					<div>
						<label for="vehicle-number-input" class="block text-xs font-bold uppercase tracking-wider text-secondary mb-1">
							{lang === 'ml' ? 'വാഹന നമ്പർ (ബാധകമെങ്കിൽ)' : 'Vehicle Registration No. (If applicable)'}
						</label>
						<input 
							id="vehicle-number-input"
							type="text" 
							bind:value={vehicleNumber} 
							oninput={triggerAutoSave}
							placeholder="KL-07-CC-4521" 
							class="w-full px-3.5 py-2.5 rounded-lg border border-surface-variant text-sm uppercase focus:ring-2 focus:ring-primary focus:border-primary bg-surface-container-lowest"
						/>
					</div>

					<div>
						<label for="licence-number-input" class="block text-xs font-bold uppercase tracking-wider text-secondary mb-1">
							{lang === 'ml' ? 'ഡ്രൈവിംഗ് ലൈസൻസ് നമ്പർ' : 'Driving Licence No.'}
						</label>
						<input 
							id="licence-number-input"
							type="text" 
							bind:value={licenceNumber} 
							oninput={triggerAutoSave}
							placeholder="KL1420110001234" 
							class="w-full px-3.5 py-2.5 rounded-lg border border-surface-variant text-sm uppercase focus:ring-2 focus:ring-primary focus:border-primary bg-surface-container-lowest"
						/>
					</div>

					<!-- Identity Verification (DPDP Compliant) -->
					<div class="sm:col-span-2 pt-2 border-t border-surface-variant">
						<div class="flex items-center justify-between mb-2">
							<label for="id-last-digits-input" class="block text-xs font-bold uppercase tracking-wider text-secondary">
								{lang === 'ml' ? 'തിരിച്ചറിയൽ രേഖ സ്ഥിരീകരണം' : 'Government ID Verification'} <span class="text-primary">*</span>
							</label>
							<span class="text-[11px] font-semibold text-green-700 bg-green-50 px-2 py-0.5 rounded border border-green-200">
								DPDP Act Compliant
							</span>
						</div>

						<div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
							<div>
								<select 
									bind:value={idDocType} 
									class="w-full px-3.5 py-2.5 rounded-lg border border-surface-variant text-sm focus:ring-2 focus:ring-primary focus:border-primary bg-surface-container-lowest"
								>
									<option value="Aadhaar">Aadhaar Card (ആധാർ)</option>
									<option value="Voter ID">Voter ID (തിരിച്ചറിയൽ കാർഡ്)</option>
									<option value="Driving Licence">Driving Licence</option>
								</select>
							</div>
							<div class="sm:col-span-2">
								<input 
									id="id-last-digits-input"
									type="text" 
									bind:value={idLastDigits} 
									oninput={triggerAutoSave}
									maxlength="4" 
									placeholder={lang === 'ml' ? 'അവസാന 4 അക്കങ്ങൾ മാത്രം നൽകുക (ഉദാ: 5678)' : 'Enter last 4 digits only (e.g. 5678)'} 
									required 
									class="w-full px-3.5 py-2.5 rounded-lg border border-surface-variant text-sm tracking-wider font-mono focus:ring-2 focus:ring-primary focus:border-primary bg-surface-container-lowest"
								/>
							</div>
						</div>
						<p class="text-[11px] text-secondary mt-1.5">
							{lang === 'ml'
								? 'സ്വകാര്യത സംരക്ഷിക്കാൻ ആധാർ നമ്പർ പൂർണ്ണമായി സൂക്ഷിക്കില്ല, അവസാന 4 അക്കങ്ങൾ മാത്രം നൽകുക.'
								: 'For data privacy protection, the union will never store your full 12-digit Aadhaar number.'}
						</p>
					</div>
				</div>

				<div class="pt-4 flex justify-between border-t border-slate-200">
					<button 
						type="button" 
						onclick={() => activeStep = 2} 
						class="px-5 py-2.5 border border-slate-300 text-slate-700 font-semibold rounded-xl hover:bg-slate-50 text-sm shadow-xs"
					>
						{lang === 'ml' ? 'പിന്നോട്ട്' : 'Back'}
					</button>
					<button 
						type="button" 
						onclick={validateStep3} 
						class="px-7 py-2.5 crimson-gradient-btn text-white font-bold rounded-xl text-sm shadow-md"
					>
						{lang === 'ml' ? 'തുടരുക' : 'Continue'}
					</button>
				</div>
			</section>
		{/if}

		<!-- STEP 4: Live Selfie & Declaration -->
		{#if activeStep === 4}
			<section class="space-y-6">
				<div>
					<h2 class="text-xl font-bold text-on-surface flex items-center gap-2">
						<span class="material-symbols-outlined text-primary">photo_camera</span>
						<span>{lang === 'ml' ? 'തത്സമയ ഫോട്ടോ (സെൽഫി)' : 'Live In-App Selfie Capture'}</span>
					</h2>
					<p class="text-sm text-secondary mt-1">
						{lang === 'ml' 
							? 'ഈ ഫോട്ടോ നിങ്ങളുടെ ഔദ്യോഗിക യൂണിയൻ ഐഡി കാർഡിൽ പ്രിന്റ് ചെയ്യുന്നതാണ്.' 
							: 'This photo will appear directly on your official digital trade union ID card.'}
					</p>
				</div>

				<!-- Camera Viewfinder & Preview -->
				<div class="flex flex-col items-center justify-center p-6 bg-surface-container-low border-2 border-dashed border-surface-variant rounded-xl space-y-4">
					{#if cameraActive}
						<div class="relative w-64 h-64 bg-black rounded-xl overflow-hidden shadow-inner">
							<!-- svelte-ignore a11y_media_has_caption -->
							<video bind:this={videoElement} autoplay playsinline class="w-full h-full object-cover"></video>
							<div class="absolute inset-0 border-2 border-white/60 rounded-full m-6 pointer-events-none border-dashed animate-pulse"></div>
						</div>
					{:else if capturedPhoto}
						<div class="w-64 h-64 bg-surface-container rounded-xl overflow-hidden shadow-md border-2 border-primary">
							<img src={capturedPhoto} alt="Captured selfie" class="w-full h-full object-cover" />
						</div>
					{:else}
						<div class="text-center py-6">
							<div class="w-16 h-16 rounded-full bg-primary-fixed text-primary mx-auto flex items-center justify-center mb-3">
								<span class="material-symbols-outlined text-3xl">photo_camera</span>
							</div>
							<p class="text-sm font-semibold text-on-surface">
								{lang === 'ml' ? 'ഫോൺ ക്യാമറ വഴി തത്സമയ ഫോട്ടോ എടുക്കുക' : 'Take a live photo using your phone camera'}
							</p>
							<p class="text-xs text-secondary mt-1">
								{lang === 'ml' ? 'നല്ല വെളിച്ചത്തിൽ കണ്ണടയില്ലാതെ ഫോട്ടോ എടുക്കുക' : 'Position your face in good light without sunglasses'}
							</p>
						</div>
					{/if}

					<!-- Action Buttons -->
					<div class="flex flex-wrap gap-3 justify-center">
						{#if !cameraActive && !capturedPhoto}
							<button 
								type="button" 
								onclick={startCamera} 
								class="px-4 py-2.5 bg-on-surface hover:bg-black text-on-primary text-xs font-semibold rounded-lg shadow-sm flex items-center gap-2"
							>
								<span class="material-symbols-outlined text-[16px]">videocam</span>
								<span>{lang === 'ml' ? 'ക്യാമറ തുറക്കുക' : 'Open Camera'}</span>
							</button>
							<label class="px-4 py-2.5 border border-surface-variant bg-surface-container-lowest text-secondary text-xs font-semibold rounded-lg hover:bg-surface-container flex items-center gap-1.5 cursor-pointer">
								<span class="material-symbols-outlined text-[16px]">upload</span>
								<span>{lang === 'ml' ? 'ഫോട്ടോ അപ്‌ലോഡ് ചെയ്യുക' : 'Upload Photo'}</span>
								<input type="file" accept="image/*" class="hidden" onchange={handleFileUpload} />
							</label>
						{:else if cameraActive}
							<button 
								type="button" 
								onclick={capturePhoto} 
								class="px-5 py-2.5 bg-primary hover:bg-primary-container text-on-primary text-xs font-semibold rounded-lg shadow-sm flex items-center gap-2"
							>
								<span class="material-symbols-outlined text-[16px]">camera</span>
								<span>{lang === 'ml' ? 'ഫോട്ടോ പകർത്തുക' : 'Capture Photo'}</span>
							</button>
							<button 
								type="button" 
								onclick={stopCamera} 
								class="px-4 py-2.5 border border-surface-variant bg-surface-container-lowest text-secondary text-xs font-semibold rounded-lg"
							>
								{lang === 'ml' ? 'റദ്ദാക്കുക' : 'Cancel'}
							</button>
						{:else if capturedPhoto}
							<button 
								type="button" 
								onclick={retakePhoto} 
								class="px-4 py-2.5 border border-surface-variant bg-surface-container-lowest text-secondary text-xs font-semibold rounded-lg hover:bg-surface-container flex items-center gap-1.5"
							>
								<span class="material-symbols-outlined text-[16px]">refresh</span>
								<span>{lang === 'ml' ? 'വീണ്ടും എടുക്കുക' : 'Retake'}</span>
							</button>
						{/if}
					</div>
				</div>

				<!-- Statutory Consent & Declaration -->
				<div class="bg-surface-container-low p-5 rounded-xl border border-surface-variant space-y-3">
					<h3 class="text-xs font-bold uppercase tracking-wider text-on-surface flex items-center gap-1.5">
						<span class="material-symbols-outlined text-[18px] text-primary">verified_user</span>
						<span>{lang === 'ml' ? 'സത്യപ്രസ്താവനയും സ്വകാര്യതാ സമ്മതവും' : 'Union Declaration & Privacy Consent'}</span>
					</h3>
					<div class="text-xs text-secondary leading-relaxed space-y-2 max-h-36 overflow-y-auto p-3 bg-surface-container-lowest rounded border border-surface-variant">
						<p>
							<strong>1. Union Constitution:</strong> I hereby declare that I am an active gig/platform worker in Kerala and willingly accept the constitution and discipline of the Kerala Gig & Platform Workers Union (affiliated to CITU).
						</p>
						<p>
							<strong>2. Data Usage:</strong> I consent to the Union collecting and processing my details to maintain my digital membership card, organize grievance redressal with platform aggregators, and allocate my record to my district committee under DPDP Act provisions.
						</p>
						<p>
							<strong>3. Fee Acknowledgement:</strong> I understand that a one-time registration fee of <strong>₹100</strong> will be charged upon completing this form.
						</p>
					</div>

					<label class="flex items-start gap-2.5 pt-1 cursor-pointer">
						<input 
							type="checkbox" 
							bind:checked={consentAgreed} 
							required 
							class="mt-0.5 w-4 h-4 text-primary rounded border-surface-variant focus:ring-primary"
						/>
						<span class="text-xs font-semibold text-on-surface">
							{lang === 'ml'
								? 'മേൽപറഞ്ഞ വിവരങ്ങൾ സത്യമാണെന്നും യൂണിയൻ ചട്ടങ്ങൾ പാലിക്കാമെന്നും ഞാൻ സമ്മതിക്കുന്നു.'
								: 'I have read, understood, and accept the union declaration and privacy terms.'}
						</span>
					</label>
				</div>

				<!-- Submit to Payment -->
				<div class="pt-4 flex justify-between border-t border-slate-200">
					<button 
						type="button" 
						onclick={() => activeStep = 3} 
						class="px-5 py-2.5 border border-slate-300 text-slate-700 font-semibold rounded-xl hover:bg-slate-50 text-sm shadow-xs"
					>
						{lang === 'ml' ? 'പിന്നോട്ട്' : 'Back'}
					</button>
					<button 
						type="button" 
						onclick={proceedToPayment} 
						disabled={submitting}
						class="px-7 py-3 crimson-gradient-btn text-white font-bold rounded-xl text-sm shadow-lg flex items-center gap-2 disabled:opacity-50"
					>
						<span>{lang === 'ml' ? 'പേയ്‌മെന്റിലേക്ക് പോകുക (₹100)' : 'Proceed to Payment (₹100)'}</span>
						<span class="material-symbols-outlined text-[18px]">arrow_forward</span>
					</button>
				</div>
			</section>
		{/if}
	</div>

	<!-- Support Help Card -->
	<div class="mt-8 card-gloss rounded-2xl p-4 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-600 gap-3 shadow-sm">
		<div class="flex items-center gap-2">
			<span class="material-symbols-outlined text-[20px] text-primary shrink-0">help</span>
			<span>{lang === 'ml' ? 'രജിസ്ട്രേഷനിൽ സഹായം വേണമോ? ജില്ലാ യൂണിയൻ പ്രതിനിധിയുമായി ബന്ധപ്പെടുക.' : 'Need assistance with registration? Contact your district union representative.'}</span>
		</div>
		<a href="/#quick-access-banner" class="text-primary font-bold hover:underline flex items-center gap-1 shrink-0">
			<span>{lang === 'ml' ? '14 ജില്ലാ ഹെൽപ്പ്‌ലൈനുകൾ' : 'View 14 District Helplines'}</span>
			<span class="material-symbols-outlined text-[16px]">chevron_right</span>
		</a>
	</div>
</main>
</div>

<!-- Footer -->
<footer class="bg-slate-900 text-slate-400 border-t border-slate-800 py-8">
	<div class="max-w-5xl mx-auto px-4 text-center text-xs">
		<p class="font-bold text-white">Kerala Gig & Platform Workers Union (affiliated to CITU)</p>
		<p class="mt-1 text-slate-400">Technical Platform developed with DYFI Professional Committee Kerala · Version 1.0 (2026)</p>
	</div>
</footer>
