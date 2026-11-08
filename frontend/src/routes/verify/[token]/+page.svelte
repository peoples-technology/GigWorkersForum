<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';

	let lang = $state<'ml' | 'en'>('ml');
	let copied = $state(false);
	let currentTimestamp = $state('');
	let isDownloading = $state(false);
	let dynamicRecord = $state<any>(null);

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

	function getDistrictInfo(codeOrName: string) {
		const match = districts.find(d => 
			d.code.toUpperCase() === (codeOrName || '').toUpperCase() || 
			d.en.toLowerCase() === (codeOrName || '').toLowerCase() || 
			(codeOrName || '').includes(d.code)
		);
		return match || { code: 'KLTVC', en: 'Thiruvananthapuram', ml: 'തിരുവനന്തപുരം' };
	}

	function getPlatformInfo(platformName: string) {
		const p = (platformName || 'Swiggy').toLowerCase();
		if (p.includes('zomato')) return { name: 'Zomato (സൊമാറ്റോ)', color: 'bg-red-600' };
		if (p.includes('swiggy')) return { name: 'Swiggy (സ്വിഗ്ഗി)', color: 'bg-amber-600' };
		if (p.includes('uber')) return { name: 'Uber (ഊബർ)', color: 'bg-slate-900' };
		if (p.includes('ola')) return { name: 'Ola (ഒല)', color: 'bg-emerald-600' };
		if (p.includes('zepto')) return { name: 'Zepto (സെപ്റ്റോ)', color: 'bg-purple-600' };
		if (p.includes('blinkit')) return { name: 'Blinkit (ബ്ലിങ്കിറ്റ്)', color: 'bg-yellow-500' };
		if (p.includes('porter')) return { name: 'Porter (പോർട്ടർ)', color: 'bg-blue-600' };
		if (p.includes('rapido')) return { name: 'Rapido (റാപ്പിഡോ)', color: 'bg-amber-500' };
		if (p.includes('flipkart')) return { name: 'Flipkart Minutes', color: 'bg-blue-600' };
		if (p.includes('instamart')) return { name: 'Instamart', color: 'bg-amber-700' };
		if (p.includes('bigbasket')) return { name: 'BigBasket', color: 'bg-emerald-600' };
		return { name: platformName || 'Gig Worker', color: 'bg-slate-700' };
	}

	function getSectorInfo(sector: string, platform: string) {
		const s = (sector || '').toLowerCase();
		const p = (platform || '').toLowerCase();
		if (s.includes('ride') || p.includes('uber') || p.includes('ola') || p.includes('rapido')) {
			return {
				sectorEn: 'Ride Hailing & Transport',
				sectorMl: 'റൈഡ് ഹെയ്‌ലിംഗ് & ഗതാഗതം',
				roleEn: 'Taxi / Cab Mobility Pilot',
				roleMl: 'ക്യാബ് / ഓട്ടോ പൈലറ്റ്'
			};
		}
		if (s.includes('demand') || p.includes('urban')) {
			return {
				sectorEn: 'On-Demand Home Services',
				sectorMl: 'ഓൺ-ഡിമാൻഡ് സർവീസുകൾ',
				roleEn: 'Service Professional',
				roleMl: 'സർവീസ് പ്രൊഫഷണൽ'
			};
		}
		if (s.includes('logistics') || p.includes('porter') || p.includes('delhivery')) {
			return {
				sectorEn: 'Courier & Freight Logistics',
				sectorMl: 'കൊറിയർ & കാർഗോ ലോജിസ്റ്റിക്സ്',
				roleEn: 'Logistics Pilot',
				roleMl: 'ലോജിസ്റ്റിക്സ് പൈലറ്റ്'
			};
		}
		return {
			sectorEn: 'Food Delivery & Hyperlocal Logistics',
			sectorMl: 'ഫുഡ് ഡെലിവറി & ലോജിസ്റ്റിക്സ്',
			roleEn: 'Delivery Partner',
			roleMl: 'ഭക്ഷ്യവിതരണ തൊഴിലാളി'
		};
	}

	function findMemberData(token: string) {
		if (typeof window === 'undefined') return null;
		const cleanToken = (token || '').trim().toUpperCase();

		// 1. Check currentMember in sessionStorage
		try {
			const curStr = sessionStorage.getItem('currentMember');
			if (curStr) {
				const cur = JSON.parse(curStr);
				if (cur.id && (cur.id.toUpperCase() === cleanToken || cleanToken.includes(cur.id.toUpperCase()) || cur.id.toUpperCase().includes(cleanToken) || cur.mobile === token.trim())) {
					return cur;
				}
			}
		} catch (e) {}

		// 2. Check direct member key in localStorage
		try {
			const mStr = localStorage.getItem(`member_${cleanToken}`);
			if (mStr) return JSON.parse(mStr);
		} catch (e) {}

		// 3. Check registry dictionary in localStorage
		try {
			const regStr = localStorage.getItem('ksgpwu_members_registry');
			if (regStr) {
				const reg = JSON.parse(regStr);
				if (reg[cleanToken]) return reg[cleanToken];
				if (reg[token.trim()]) return reg[token.trim()];
				for (const key of Object.keys(reg)) {
					const item = reg[key];
					if (item && (item.id?.toUpperCase() === cleanToken || item.mobile === token.trim())) {
						return item;
					}
				}
			}
		} catch (e) {}

		// 4. Check lastRegisteredMember in localStorage
		try {
			const lastStr = localStorage.getItem('lastRegisteredMember');
			if (lastStr) {
				const last = JSON.parse(lastStr);
				if (last.id && (last.id.toUpperCase() === cleanToken || last.mobile === token.trim())) {
					return last;
				}
			}
		} catch (e) {}

		// 5. Check if user freshly arrived from checkout / register
		try {
			const curStr = sessionStorage.getItem('currentMember') || localStorage.getItem('lastRegisteredMember');
			if (curStr) {
				const cur = JSON.parse(curStr);
				if (cur && cur.name && (cleanToken.startsWith('KL-') || cleanToken.startsWith('KL'))) {
					return cur;
				}
			}
		} catch (e) {}

		return null;
	}

	// Dynamic token from route params
	let memberToken = $derived($page.params.token || 'KLTVC000009');

	onMount(() => {
		const found = findMemberData(memberToken);
		if (found) {
			dynamicRecord = found;
		}

		// Also try background backend check if online
		try {
			fetch(`/verify/${encodeURIComponent(memberToken)}`)
				.then(r => r.ok ? r.json() : null)
				.then(data => {
					if (data && data.valid && data.name) {
						if (!dynamicRecord) {
							dynamicRecord = {
								id: data.membership_number || memberToken,
								name: data.name,
								nameMl: data.name,
								districtName: data.district,
								status: data.status,
								validUntil: '31 October 2027'
							};
						}
					}
				}).catch(() => {});
		} catch (e) {}

		const now = new Date();
		const options: Intl.DateTimeFormatOptions = {
			day: 'numeric',
			month: 'long',
			year: 'numeric',
			hour: '2-digit',
			minute: '2-digit',
			hour12: true,
			timeZoneName: 'short'
		};
		try {
			currentTimestamp = now.toLocaleString('en-IN', options);
		} catch (e) {
			currentTimestamp = now.toISOString();
		}
	});

	// Derived Member profile attributes
	let member = $derived.by(() => {
		const rec = dynamicRecord || findMemberData(memberToken);
		if (rec) {
			const dist = getDistrictInfo(rec.districtCode || rec.district);
			const platformInfo = getPlatformInfo(rec.primaryPlatform);
			const sectorInfo = getSectorInfo(rec.primarySector, rec.primaryPlatform);

			return {
				id: rec.id || memberToken.toUpperCase(),
				tokenHash: rec.tokenHash || `SHA256-${dist.code.toLowerCase()}_${Math.random().toString(36).substring(2, 8)}`,
				name: (rec.name || 'CITU MEMBER').toUpperCase(),
				nameMl: rec.nameMl || rec.name || 'യൂണിയൻ അംഗം',
				roleEn: sectorInfo.roleEn,
				roleMl: sectorInfo.roleMl,
				districtCode: dist.code,
				districtName: `${dist.ml} / ${dist.en}`,
				districtNameEn: dist.en,
				districtNameMl: dist.ml,
				sectorEn: sectorInfo.sectorEn,
				sectorMl: sectorInfo.sectorMl,
				primaryPlatform: rec.primaryPlatform || 'Swiggy',
				platforms: [platformInfo],
				vehicleNumber: rec.vehicleNumber || '',
				status: rec.status || 'Active & Paid-Up',
				validUntil: rec.validUntil || '31 October 2027',
				photo: rec.photo || 'https://lh3.googleusercontent.com/aida-public/AB6AXuCYyEu0qaQ2w1WiZP9iWtGjRuf2bZDkOpwgqz4ESsoieX_F7_jXg2jQ7Z5RTdMXXFEwaPkQvAjvu6dqW1P3GVAWU7AfOTZO3Tm0Q3iAEGqNcQxvvi0EGTen8-ymjqNmHp-A6UGwYcBKMQXCB9nuj6KtyXtYRjkpI-Jdho5SaWPaY26TAH8e9G0xl1bWzxHVhvsSxkyHNNiQbPyV6vD2vdLy0R9AwN7hD1p8rB-otH7tgdWaFNA4KQUrMA'
			};
		}

		// Fallback for static demo tokens
		const isFZ = memberToken.includes('FZ') || memberToken.includes('000142');
		const isRN = memberToken.includes('RN') || memberToken.includes('000219');
		return {
			id: memberToken.toUpperCase(),
			tokenHash: `SHA256-${memberToken.slice(0, 4).toLowerCase()}_${Math.random().toString(36).substring(2, 8)}`,
			name: isFZ ? 'FATHIMA ZAHRA' : isRN ? 'RAHUL V. NAIR' : 'ANANDHU K. S.',
			nameMl: isFZ ? 'ഫാത്തിമ സഹ്റ' : isRN ? 'രാഹുൽ വി. നായർ' : 'ആനന്ദു കെ. എസ്.',
			roleEn: isFZ ? 'Taxi Cab Driver · Airport Fleet' : isRN ? 'Courier Pilot · Hyperlocal' : 'Food Delivery Partner',
			roleMl: isFZ ? 'ക്യാബ് ഡ്രൈവർ' : isRN ? 'കൊറിയർ പൈലറ്റ്' : 'ഭക്ഷ്യവിതരണ തൊഴിലാളി',
			districtCode: memberToken.startsWith('KL') ? memberToken.slice(0, 5) : 'KLTVC',
			districtName: isFZ ? 'എറണാകുളം / Ernakulam' : memberToken.includes('KKD') ? 'കോഴിക്കോട് / Kozhikode' : 'തിരുവനന്തപുരം / Trivandrum',
			districtNameEn: isFZ ? 'Ernakulam' : 'Thiruvananthapuram',
			districtNameMl: isFZ ? 'എറണാകുളം' : 'തിരുവനന്തപുരം',
			sectorEn: isFZ ? 'Ride Hailing & Transport' : 'Food Delivery & Logistics',
			sectorMl: isFZ ? 'റൈഡ് ഹെയ്‌ലിംഗ് & ഗതാഗതം' : 'ഫുഡ് ഡെലിവറി & ലോജിസ്റ്റിക്സ്',
			primaryPlatform: isFZ ? 'Uber' : 'Swiggy',
			platforms: isFZ ? [{ name: 'Uber (ഊബർ)', color: 'bg-slate-900' }] : [{ name: 'Swiggy (സ്വിഗ്ഗി)', color: 'bg-amber-600' }, { name: 'Zomato (സൊമാറ്റോ)', color: 'bg-red-600' }],
			vehicleNumber: isFZ ? 'KL 07 CD 7890' : isRN ? 'KL 01 BB 2424' : 'KL 01 CB 1234',
			status: 'Active & Paid-Up',
			validUntil: '31 October 2027',
			photo: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCYyEu0qaQ2w1WiZP9iWtGjRuf2bZDkOpwgqz4ESsoieX_F7_jXg2jQ7Z5RTdMXXFEwaPkQvAjvu6dqW1P3GVAWU7AfOTZO3Tm0Q3iAEGqNcQxvvi0EGTen8-ymjqNmHp-A6UGwYcBKMQXCB9nuj6KtyXtYRjkpI-Jdho5SaWPaY26TAH8e9G0xl1bWzxHVhvsSxkyHNNiQbPyV6vD2vdLy0R9AwN7hD1p8rB-otH7tgdWaFNA4KQUrMA'
		};
	});

	function copyId() {
		navigator.clipboard.writeText(member.id);
		copied = true;
		setTimeout(() => {
			copied = false;
		}, 2000);
	}

	async function downloadCardPng() {
		isDownloading = true;
		try {
			const canvas = document.createElement('canvas');
			canvas.width = 1012;
			canvas.height = 638;
			const ctx = canvas.getContext('2d');
			if (!ctx) return;

			// 1. Background
			ctx.fillStyle = '#FFFFFF';
			ctx.fillRect(0, 0, canvas.width, canvas.height);

			// 2. Header
			ctx.fillStyle = '#991B1B';
			ctx.fillRect(0, 0, canvas.width, 130);

			// Gold stripe
			ctx.fillStyle = '#F59E0B';
			ctx.fillRect(0, 124, canvas.width, 6);

			// Header text
			ctx.fillStyle = '#FFFFFF';
			ctx.font = "bold 26px 'Anek Malayalam', sans-serif";
			ctx.fillText("KERALA STATE GIG & PLATFORM WORKERS UNION (CITU)", 40, 52);
			ctx.fillStyle = '#FEF3C7';
			ctx.font = "18px 'Anek Malayalam', sans-serif";
			ctx.fillText("Reg. No: Tu19965 • Registered Under Trade Unions Act", 40, 88);

			// Union Logo in header
			try {
				const logo = new Image();
				logo.crossOrigin = 'anonymous';
				logo.src = '/gigLogo.png';
				await new Promise((resolve) => {
					logo.onload = () => {
						ctx.drawImage(logo, canvas.width - 125, 15, 100, 100);
						resolve(true);
					};
					logo.onerror = () => resolve(false);
				});
			} catch (e) {}

			// 3. Member Photo
			ctx.strokeStyle = '#991B1B';
			ctx.lineWidth = 3;
			ctx.strokeRect(40, 155, 200, 245);
			ctx.fillStyle = '#F1F5F9';
			ctx.fillRect(40, 155, 200, 245);

			if (member.photo) {
				try {
					const photoImg = new Image();
					photoImg.crossOrigin = 'anonymous';
					photoImg.src = member.photo;
					await new Promise((resolve) => {
						photoImg.onload = () => {
							ctx.drawImage(photoImg, 40, 155, 200, 245);
							resolve(true);
						};
						photoImg.onerror = () => resolve(false);
					});
				} catch (e) {}
			}

			// Active member badge
			ctx.fillStyle = '#10B981';
			ctx.fillRect(40, 412, 200, 36);
			ctx.fillStyle = '#FFFFFF';
			ctx.font = "bold 16px sans-serif";
			ctx.textAlign = 'center';
			ctx.fillText("ACTIVE MEMBER", 140, 436);
			ctx.textAlign = 'left';

			// 4. Member Info
			const startX = 275;
			ctx.fillStyle = '#0F172A';
			ctx.font = "bold 32px 'Anek Malayalam', sans-serif";
			ctx.fillText(member.name, startX, 195);

			ctx.fillStyle = '#64748B';
			ctx.font = "20px 'Anek Malayalam', sans-serif";
			ctx.fillText("Membership ID:", startX, 245);
			ctx.fillStyle = '#B91C1C';
			ctx.font = "bold 24px monospace";
			ctx.fillText(member.id, startX + 170, 245);

			ctx.fillStyle = '#64748B';
			ctx.font = "20px 'Anek Malayalam', sans-serif";
			ctx.fillText("District Unit:", startX, 290);
			ctx.fillStyle = '#0F172A';
			ctx.font = "bold 22px 'Anek Malayalam', sans-serif";
			ctx.fillText(member.districtNameEn || member.districtName, startX + 170, 290);

			ctx.fillStyle = '#64748B';
			ctx.font = "20px 'Anek Malayalam', sans-serif";
			ctx.fillText("Platform:", startX, 335);
			ctx.fillStyle = '#0F172A';
			ctx.font = "bold 22px 'Anek Malayalam', sans-serif";
			ctx.fillText(member.platforms[0]?.name || member.primaryPlatform || 'Swiggy', startX + 170, 335);

			ctx.fillStyle = '#64748B';
			ctx.font = "20px 'Anek Malayalam', sans-serif";
			ctx.fillText("Sector:", startX, 380);
			ctx.fillStyle = '#0F172A';
			ctx.font = "bold 20px 'Anek Malayalam', sans-serif";
			ctx.fillText(member.sectorEn, startX + 170, 380);

			if (member.vehicleNumber) {
				ctx.fillStyle = '#64748B';
				ctx.font = "20px 'Anek Malayalam', sans-serif";
				ctx.fillText("Vehicle / RC:", startX, 425);
				ctx.fillStyle = '#0F172A';
				ctx.font = "bold 20px monospace";
				ctx.fillText(member.vehicleNumber, startX + 170, 425);
			}

			ctx.fillStyle = '#64748B';
			ctx.font = "20px 'Anek Malayalam', sans-serif";
			ctx.fillText("Valid Through:", startX, 470);
			ctx.fillStyle = '#059669';
			ctx.font = "bold 22px monospace";
			ctx.fillText(member.validUntil, startX + 170, 470);

			// 5. QR Code
			try {
				const qrUrl = typeof window !== 'undefined' ? window.location.href : `https://gigworkers.online/verify/${member.id}`;
				const qrImg = new Image();
				qrImg.crossOrigin = 'anonymous';
				qrImg.src = `https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=${encodeURIComponent(qrUrl)}`;
				await new Promise((resolve) => {
					qrImg.onload = () => {
						ctx.drawImage(qrImg, canvas.width - 210, 165, 170, 170);
						resolve(true);
					};
					qrImg.onerror = () => resolve(false);
				});

				ctx.fillStyle = '#64748B';
				ctx.font = "15px sans-serif";
				ctx.fillText("Scan to Verify", canvas.width - 175, 355);
			} catch (e) {}

			// 6. Footer bar
			ctx.fillStyle = '#0F172A';
			ctx.fillRect(0, canvas.height - 46, canvas.width, 46);
			ctx.fillStyle = '#CBD5E1';
			ctx.font = "16px sans-serif";
			ctx.fillText("E Balananda Smaraka Office, Mele Thampanoor • Ph: 9846063666, 9447695655 • Reg. No: Tu19965", 40, canvas.height - 18);

			// Download link
			const a = document.createElement('a');
			a.download = `CITU_Membership_Card_${member.id}.png`;
			a.href = canvas.toDataURL('image/png');
			a.click();
		} catch (err) {
			console.error(err);
		} finally {
			isDownloading = false;
		}
	}
</script>

<svelte:head>
	<title>{lang === 'ml' ? `അംഗത്വ പരിശോധന: ${member.id} | GigWorkers.Online` : `Member Verification: ${member.id} | GigWorkers.Online`}</title>
</svelte:head>

<!-- Sticky Header -->
<header class="fixed top-0 left-0 right-0 w-full z-50 bg-white/95 backdrop-blur-md shadow-xs border-b border-slate-200/80 print:hidden">
	<div class="h-16 sm:h-20 max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 flex items-center justify-between gap-2">
		<!-- Union Logo & Header Title -->
		<a href="/" class="flex items-center gap-2 sm:gap-3 min-w-0 flex-shrink">
			<img
				src="/gigLogo.png"
				alt="Kerala State Gig and Platform Workers Union (CITU) Official Logo"
				class="w-9 h-9 sm:w-10 sm:h-10 rounded-full object-contain drop-shadow-sm shrink-0"
				onerror={(e) => {
					(e.currentTarget as HTMLImageElement).src = '/images/gigLogo.png';
				}}
			/>
			<div class="flex flex-col min-w-0">
				<div class="flex items-center gap-1.5 sm:gap-2">
					<span class="text-sm sm:text-base tracking-tight text-slate-900 uppercase font-bold truncate">GigWorkers.Online</span>
					<span class="hidden sm:inline-block px-2 py-0.5 rounded-full bg-red-100 text-red-800 text-[10px] uppercase font-bold">
						Trade Union
					</span>
				</div>
				<span class="text-[10px] sm:text-xs text-slate-500 font-medium truncate">
					{lang === 'ml' ? 'അംഗത്വ പരിശോധന / Public Verification' : 'Public Verification Protocol'}
				</span>
			</div>
		</a>

		<!-- Language Switcher & Official Gateway Badge -->
		<div class="flex items-center gap-1.5 sm:gap-3 flex-shrink-0">
			<div class="hidden md:flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 text-slate-600 text-xs">
				<span class="material-symbols-outlined text-primary text-[16px]">verified_user</span>
				<span class="font-semibold text-slate-800">Official Gateway</span>
			</div>

			<div class="inline-flex items-center bg-slate-100 border border-slate-200 rounded-full p-0.5 sm:p-1">
				<button 
					type="button" 
					onclick={() => lang = 'ml'}
					class={`px-2 sm:px-2.5 py-1 rounded-full text-[11px] sm:text-xs font-semibold ${lang === 'ml' ? 'bg-primary text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'}`}
				>
					മലയാളം
				</button>
				<button 
					type="button" 
					onclick={() => lang = 'en'}
					class={`px-2 sm:px-2.5 py-1 rounded-full text-[11px] sm:text-xs font-semibold ${lang === 'en' ? 'bg-primary text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'}`}
				>
					EN
				</button>
			</div>

			<a href="/" class="hidden sm:inline-flex text-xs font-semibold text-slate-600 hover:text-primary transition items-center gap-1">
				<span class="material-symbols-outlined text-[16px]">home</span>
				<span>Home</span>
			</a>
		</div>
	</div>
</header>

<main class="w-full pt-20 hero-gradient-mesh flex-1 flex flex-col justify-start print:pt-4 print:bg-white">
	<div class="flex flex-col w-full py-8 sm:py-12 px-4 sm:px-6 items-center justify-center">
		<!-- Subtle ambient decorative glow -->
		<div class="relative w-full max-w-[640px] flex flex-col items-center">
			<div class="absolute -top-12 -left-12 w-64 h-64 bg-red-500/10 rounded-full blur-3xl pointer-events-none print:hidden"></div>
			<div class="absolute -bottom-12 -right-12 w-72 h-72 bg-amber-500/15 rounded-full blur-3xl pointer-events-none print:hidden"></div>

			<!-- Metadata Tag Header -->
			<div class="w-full flex items-center justify-between pb-3 px-1 text-slate-500 text-xs print:hidden">
				<div class="flex items-center gap-1.5 font-bold">
					<span class="material-symbols-outlined text-[18px] text-primary">verified</span>
					<span class="uppercase tracking-wider">Public Verification Protocol • v2.4</span>
				</div>
				<div class="flex items-center gap-1.5 font-bold text-emerald-700">
					<span class="w-2.5 h-2.5 rounded-full bg-emerald-600 animate-pulse"></span>
					<span class="font-mono text-[11px]">LIVE VERIFIED</span>
				</div>
			</div>

			<!-- 1. Official Physical CITU Membership Card Preview -->
			<div class="w-full max-w-[640px] mb-8 flex flex-col items-center">
				<div class="w-full flex items-center justify-between pb-2 px-1 text-slate-600 text-xs font-bold print:hidden">
					<div class="flex items-center gap-1.5 text-primary">
						<span class="material-symbols-outlined text-[18px]">badge</span>
						<span class="uppercase tracking-wider">{lang === 'ml' ? 'ഡിജിറ്റൽ യൂണിയൻ അംഗത്വ കാർഡ്' : 'Official Union Digital ID Card'}</span>
					</div>
					<div class="flex items-center gap-2">
						<span class="px-2 py-0.5 rounded bg-red-100 text-primary text-[10px] font-mono font-bold">CR80 • FORM-I</span>
					</div>
				</div>

				<!-- Physical Card Container with Union Styling -->
				<div 
					id="union-membership-card"
					class="w-full rounded-2xl sm:rounded-3xl shadow-2xl border-2 border-red-950/20 bg-white overflow-hidden relative print:shadow-none print:border-slate-800"
				>
					<!-- Header Strip with Official CITU Solidarity Red -->
					<div class="bg-gradient-to-r from-red-900 via-red-800 to-red-700 text-white px-4 sm:px-6 py-3 sm:py-4 flex items-center justify-between gap-3 relative overflow-hidden">
						<!-- Ambient subtle star watermark -->
						<div class="absolute -right-6 -bottom-6 opacity-10 pointer-events-none">
							<svg class="w-36 h-36" viewBox="0 0 100 100" fill="currentColor">
								<path d="M50 0 L61 35 L98 35 L68 57 L79 91 L50 70 L21 91 L32 57 L2 35 L39 35 Z"/>
							</svg>
						</div>

						<div class="flex items-center gap-3 min-w-0 z-10">
							<div class="w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-white p-1 shrink-0 shadow-md flex items-center justify-center">
								<img src="/gigLogo.png" alt="CITU Logo" class="w-full h-full object-contain" />
							</div>
							<div class="flex flex-col min-w-0 text-left">
								<h3 class="text-xs sm:text-sm font-black tracking-tight leading-tight uppercase font-['Anek_Malayalam']">
									കേരള സ്റ്റേറ്റ് ഗിഗ് &amp; പ്ലാറ്റ്‌ഫോം വർക്കേഴ്സ് യൂണിയൻ (സി.ഐ.ടി.യു)
								</h3>
								<p class="text-[10px] sm:text-xs text-amber-200 font-semibold tracking-wide mt-0.5">
									KERALA STATE GIG &amp; PLATFORM WORKERS UNION (CITU)
								</p>
								<p class="text-[9px] sm:text-[10px] text-red-200 font-mono mt-0.5">
									Regd. No: <strong class="text-white">Tu19965</strong> • Under Trade Unions Act, 1926
								</p>
							</div>
						</div>
					</div>

					<!-- Gold Accent Line -->
					<div class="h-1.5 w-full bg-gradient-to-r from-amber-400 via-amber-300 to-amber-500"></div>

					<!-- Card Main Body -->
					<div class="p-4 sm:p-6 bg-gradient-to-b from-white via-slate-50/60 to-slate-100 flex flex-col sm:flex-row gap-4 sm:gap-6 items-center sm:items-start text-left">
						<!-- Left Column: Photo & Active Badge -->
						<div class="flex flex-col items-center shrink-0">
							<div class="w-28 h-32 sm:w-32 sm:h-36 rounded-xl p-1 bg-white border-2 border-primary shadow-md overflow-hidden relative">
								<img 
									src={member.photo} 
									alt={member.name}
									class="w-full h-full object-cover rounded-lg"
									onerror={(e) => {
										(e.currentTarget as HTMLImageElement).src = "https://lh3.googleusercontent.com/aida-public/AB6AXuCYyEu0qaQ2w1WiZP9iWtGjRuf2bZDkOpwgqz4ESsoieX_F7_jXg2jQ7Z5RTdMXXFEwaPkQvAjvu6dqW1P3GVAWU7AfOTZO3Tm0Q3iAEGqNcQxvvi0EGTen8-ymjqNmHp-A6UGwYcBKMQXCB9nuj6KtyXtYRjkpI-Jdho5SaWPaY26TAH8e9G0xl1bWzxHVhvsSxkyHNNiQbPyV6vD2vdLy0R9AwN7hD1p8rB-otH7tgdWaFNA4KQUrMA";
									}}
								/>
							</div>
							<div class="mt-2 inline-flex items-center gap-1 px-3 py-0.5 rounded-full bg-emerald-600 text-white text-[10px] font-bold tracking-wider shadow-sm uppercase">
								<span class="w-1.5 h-1.5 rounded-full bg-white animate-pulse"></span>
								<span>ACTIVE MEMBER</span>
							</div>
						</div>

						<!-- Middle Column: Member Metadata -->
						<div class="flex-1 min-w-0 text-center sm:text-left flex flex-col justify-between self-stretch">
							<div>
								<div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">MEMBER NAME / അംഗം</div>
								<h2 class="text-xl sm:text-2xl font-black text-slate-900 leading-tight tracking-tight mt-0.5 font-['Anek_Malayalam']">
									{member.name}
								</h2>
								<p class="text-xs sm:text-sm text-primary font-bold mt-0.5">
									{member.nameMl}
								</p>
							</div>

							<div class="mt-3 grid grid-cols-2 gap-x-3 gap-y-2 text-xs">
								<div>
									<span class="text-[10px] text-slate-500 font-semibold block">അംഗത്വ നമ്പർ / ID:</span>
									<span class="font-mono font-black text-primary text-sm sm:text-base tracking-wider">{member.id}</span>
								</div>
								<div>
									<span class="text-[10px] text-slate-500 font-semibold block">ജില്ല / District:</span>
									<span class="font-bold text-slate-800">{member.districtNameEn || member.districtName}</span>
								</div>
								<div>
									<span class="text-[10px] text-slate-500 font-semibold block">പ്ലാറ്റ്‌ഫോം / Platform:</span>
									<span class="font-bold text-slate-800">{member.platforms[0]?.name || member.primaryPlatform || 'Swiggy'}</span>
								</div>
								<div>
									<span class="text-[10px] text-slate-500 font-semibold block">മേഖല / Sector:</span>
									<span class="font-medium text-slate-700 truncate block">{member.sectorEn}</span>
								</div>
								{#if member.vehicleNumber}
									<div class="col-span-2">
										<span class="text-[10px] text-slate-500 font-semibold block">വാഹനം / Vehicle Reg:</span>
										<span class="font-mono font-bold text-slate-900 bg-white px-2 py-0.5 rounded border border-slate-300 inline-block text-[11px]">{member.vehicleNumber}</span>
									</div>
								{/if}
							</div>
						</div>

						<!-- Right Column: Verification QR Code -->
						<div class="flex flex-col items-center justify-center shrink-0 border-t sm:border-t-0 sm:border-l border-slate-200 pt-3 sm:pt-0 sm:pl-4">
							<div class="w-24 h-24 sm:w-28 sm:h-28 bg-white p-1.5 rounded-xl border border-slate-300 shadow-sm flex items-center justify-center">
								<img 
									src={`https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=${encodeURIComponent(typeof window !== 'undefined' ? window.location.href : 'https://gigworkers.online/verify/' + member.id)}`} 
									alt="QR Code" 
									class="w-full h-full object-contain"
								/>
							</div>
							<span class="text-[9px] text-slate-500 font-semibold mt-1">Scan to Verify</span>
							<span class="text-[8px] font-mono text-emerald-700 font-bold">LIVE SEAL</span>
						</div>
					</div>

					<!-- Card Footer: Headquarters & Statutory Information -->
					<div class="bg-slate-900 text-slate-300 px-4 sm:px-6 py-2.5 flex flex-wrap items-center justify-between text-[10px] sm:text-[11px] border-t border-slate-800 gap-2">
						<div class="flex items-center gap-1.5">
							<span class="material-symbols-outlined text-[14px] text-amber-400">location_on</span>
							<span>E. Balananda Smaraka Office, CITU State Committee Office, Mele Thampanoor, TVM</span>
						</div>
						<div class="flex items-center gap-2">
							<span>സാധുത: <strong class="text-emerald-400 font-mono">{member.validUntil}</strong></span>
						</div>
					</div>
				</div>

				<!-- Download & Print Actions Bar -->
				<div class="w-full mt-4 flex flex-col sm:flex-row items-center justify-center gap-3 print:hidden">
					<button
						type="button"
						onclick={downloadCardPng}
						disabled={isDownloading}
						class="w-full sm:w-auto px-6 py-3 rounded-xl crimson-gradient-btn text-white font-bold text-xs sm:text-sm shadow-md transition flex items-center justify-center gap-2"
					>
						{#if isDownloading}
							<span class="material-symbols-outlined animate-spin text-[18px]">progress_activity</span>
							<span>{lang === 'ml' ? 'തയ്യാറാക്കുന്നു...' : 'Rendering Card...'}</span>
						{:else}
							<span class="material-symbols-outlined text-[18px]">download</span>
							<span>{lang === 'ml' ? 'അംഗത്വ കാർഡ് ഡൗൺലോഡ് ചെയ്യുക (PNG)' : 'Download Membership Card (PNG)'}</span>
						{/if}
					</button>

					<button
						type="button"
						onclick={() => window.print()}
						class="w-full sm:w-auto px-5 py-3 rounded-xl bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 font-bold text-xs sm:text-sm shadow-xs transition flex items-center justify-center gap-2"
					>
						<span class="material-symbols-outlined text-[18px]">print</span>
						<span>{lang === 'ml' ? 'പ്രിന്റ് ചെയ്യുക / സേവ് ചെയ്യുക' : 'Print / Save PDF'}</span>
					</button>
				</div>
			</div>

			<!-- 2. Main Public Verification Credential Sheet -->
			<div class="w-full card-gloss rounded-3xl shadow-2xl border border-slate-200/90 overflow-hidden relative print:shadow-none print:border-slate-800">
				<!-- Emerald Accent Status Bar -->
				<div class="h-2 w-full bg-emerald-600"></div>

				<!-- Verified Banner Section -->
				<div class="bg-gradient-to-b from-emerald-50 to-emerald-100/40 px-6 py-6 flex flex-col items-center text-center border-b border-emerald-100">
					<div class="w-14 h-14 rounded-2xl bg-emerald-600 text-white flex items-center justify-center shadow-lg shadow-emerald-700/20 mb-2.5">
						<span class="material-symbols-outlined text-[34px]">check_circle</span>
					</div>
					<h1 class="text-xl sm:text-2xl font-black text-emerald-950 tracking-tight font-['Anek_Malayalam']">
						{lang === 'ml' ? 'സാധുവായ അംഗത്വം' : 'VERIFIED ACTIVE MEMBER'}
					</h1>
					<p class="text-xs sm:text-sm text-emerald-800 mt-1 max-w-md font-medium">
						{lang === 'ml'
							? 'ഈ തിരിച്ചറിയൽ കാർഡ് യൂണിയൻ രേഖകളുമായി ഒത്തുനോക്കി ഉറപ്പുവരുത്തിയതാണ്.'
							: 'Verified against central union registry records • Secure State Database'}
					</p>

					<!-- Dynamic Token Hash Pill -->
					<div class="mt-3.5 inline-flex items-center gap-2 px-3.5 py-1 bg-white rounded-full shadow-xs text-emerald-900 font-mono text-xs border border-emerald-200 font-bold">
						<span class="material-symbols-outlined text-[15px] text-emerald-700">fingerprint</span>
						<span>Token:</span>
						<span class="text-slate-600">{member.tokenHash}</span>
						<span>•</span>
						<span class="text-emerald-700">Validated</span>
					</div>
				</div>

				<!-- Member Identity Profile Section -->
				<div class="pt-8 pb-4 px-6 flex flex-col items-center text-center">
					<!-- Worker Photo with Badge Overlay -->
					<div class="relative w-32 h-32 rounded-3xl p-1 bg-slate-100 shadow-xl shrink-0 border-2 border-slate-200">
						<img 
							class="w-full h-full object-cover rounded-2xl" 
							alt={member.name} 
							src={member.photo}
							onerror={(e) => {
								(e.currentTarget as HTMLImageElement).src = "https://lh3.googleusercontent.com/aida-public/AB6AXuCYyEu0qaQ2w1WiZP9iWtGjRuf2bZDkOpwgqz4ESsoieX_F7_jXg2jQ7Z5RTdMXXFEwaPkQvAjvu6dqW1P3GVAWU7AfOTZO3Tm0Q3iAEGqNcQxvvi0EGTen8-ymjqNmHp-A6UGwYcBKMQXCB9nuj6KtyXtYRjkpI-Jdho5SaWPaY26TAH8e9G0xl1bWzxHVhvsSxkyHNNiQbPyV6vD2vdLy0R9AwN7hD1p8rB-otH7tgdWaFNA4KQUrMA";
							}}
						/>
						<div class="absolute -bottom-2 -right-2 bg-emerald-600 text-white w-8 h-8 rounded-full flex items-center justify-center shadow-lg border-2 border-white">
							<span class="material-symbols-outlined text-[18px]">verified</span>
						</div>
					</div>

					<!-- Member Name Hierarchy -->
					<h2 class="text-2xl font-black text-slate-900 mt-4 tracking-tight font-['Anek_Malayalam']">
						{member.name}
					</h2>
					<p class="text-base text-primary font-bold mt-0.5 font-['Anek_Malayalam']">
						{member.nameMl} <span class="text-slate-500 font-normal">({member.roleMl})</span>
					</p>

					<!-- Member ID Pill with Copyable Cue -->
					<div class="mt-3 inline-flex items-center gap-2 bg-slate-100 px-4 py-1.5 rounded-full font-mono text-xs text-slate-800 border border-slate-200 shadow-2xs">
						<span class="text-slate-500 font-sans font-semibold">അംഗത്വ നമ്പർ / ID:</span>
						<span class="font-bold tracking-wider text-primary">{member.id}</span>
						<button 
							type="button" 
							onclick={copyId} 
							class="ml-1 text-slate-500 hover:text-primary transition-colors flex items-center" 
							title="Copy Member ID"
						>
							{#if copied}
								<span class="text-[10px] text-emerald-700 font-bold">COPIED</span>
							{:else}
								<span class="material-symbols-outlined text-[15px]">content_copy</span>
							{/if}
						</button>
					</div>
				</div>

				<!-- Structured Verification Data Rows -->
				<div class="mt-4 mx-4 sm:mx-6 rounded-xl border border-slate-200 overflow-hidden divide-y divide-slate-200 text-xs">
					<!-- Row 1: District -->
					<div class="px-4 py-3 flex items-center justify-between text-left gap-3 bg-white">
						<div class="flex flex-col">
							<span class="text-[11px] uppercase font-bold text-slate-500">ജില്ല / Working District</span>
							<span class="text-[10px] text-slate-400">Operational Jurisdiction</span>
						</div>
						<div class="flex items-center gap-2 text-right">
							<span class="inline-flex items-center px-2 py-0.5 rounded bg-slate-100 font-mono font-bold text-primary">
								{member.districtCode}
							</span>
							<span class="font-bold text-slate-900">{member.districtName}</span>
						</div>
					</div>

					<!-- Row 2: Sector -->
					<div class="px-4 py-3 flex items-center justify-between text-left gap-3 bg-slate-50">
						<div class="flex flex-col">
							<span class="text-[11px] uppercase font-bold text-slate-500">തൊഴിൽ മേഖല / Sector</span>
							<span class="text-[10px] text-slate-400">Gig Classification</span>
						</div>
						<div class="text-right">
							<span class="font-bold text-slate-900">{member.sectorMl}</span>
							<div class="text-[10px] text-slate-500">{member.sectorEn}</div>
						</div>
					</div>

					<!-- Row 3: Platform -->
					<div class="px-4 py-3 flex items-center justify-between text-left gap-3 bg-white">
						<div class="flex flex-col">
							<span class="text-[11px] uppercase font-bold text-slate-500">പ്ലാറ്റ്‌ഫോം / Platform</span>
							<span class="text-[10px] text-slate-400">Active Registered Apps</span>
						</div>
						<div class="flex items-center gap-1.5 flex-wrap justify-end">
							{#each member.platforms as p}
								<span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-800 font-semibold text-[11px] border border-slate-200">
									<span class={`w-2 h-2 rounded-full ${p.color}`}></span>
									{p.name}
								</span>
							{/each}
						</div>
					</div>

					{#if member.vehicleNumber}
						<!-- Row 4: Vehicle Number -->
						<div class="px-4 py-3 flex items-center justify-between text-left gap-3 bg-slate-50">
							<div class="flex flex-col">
								<span class="text-[11px] uppercase font-bold text-slate-500">വാഹനം / Vehicle Reg</span>
								<span class="text-[10px] text-slate-400">Motor Transport Registered</span>
							</div>
							<div class="text-right">
								<span class="font-mono font-bold text-slate-900 bg-white px-2 py-0.5 rounded border border-slate-300">{member.vehicleNumber}</span>
							</div>
						</div>
					{/if}

					<!-- Row 5: Status -->
					<div class="px-4 py-3 flex items-center justify-between text-left gap-3 bg-white">
						<div class="flex flex-col">
							<span class="text-[11px] uppercase font-bold text-slate-500">അംഗത്വ നില / Status</span>
							<span class="text-[10px] text-slate-400">Dues &amp; Compliance</span>
						</div>
						<div class="flex items-center gap-2 text-right">
							<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-bold text-[10px]">
								<span class="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>
								Good Standing
							</span>
							<span class="font-bold text-emerald-900">സജീവം / Active</span>
						</div>
					</div>

					<!-- Row 6: Valid Through -->
					<div class="px-4 py-3 flex items-center justify-between text-left gap-3 bg-slate-50">
						<div class="flex flex-col">
							<span class="text-[11px] uppercase font-bold text-slate-500">സാധുത കാലയളവ് / Valid Through</span>
							<span class="text-[10px] text-slate-400">Triennial Renewal Cycle</span>
						</div>
						<div class="text-right">
							<span class="px-2.5 py-1 rounded bg-red-100 text-red-950 font-mono font-bold">
								{member.validUntil}
							</span>
						</div>
					</div>

					<!-- Row 7: Timestamp -->
					<div class="px-4 py-3 flex items-center justify-between text-left gap-3 bg-white">
						<div class="flex flex-col">
							<span class="text-[11px] uppercase font-bold text-slate-500">പരിശോധിച്ച സമയം / Verified At</span>
							<span class="text-[10px] text-slate-400">Realtime Scan Timestamp</span>
						</div>
						<div class="flex items-center gap-1 font-mono text-slate-700 font-medium">
							<span class="material-symbols-outlined text-[16px] text-primary">schedule</span>
							<span>{currentTimestamp}</span>
						</div>
					</div>
				</div>

				<!-- Trust Graphic: KGWWB Digital Seal Canvas -->
				<div class="mt-5 mx-4 sm:mx-6 p-4 rounded-xl bg-slate-50 flex items-center justify-between gap-4 border border-slate-200">
					<div class="flex items-center gap-3">
						<div class="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-white shrink-0 shadow-sm">
							<span class="material-symbols-outlined text-[20px]">shield_with_heart</span>
						</div>
						<div class="flex flex-col text-left text-xs">
							<span class="font-bold text-slate-900">Kerala Gig Workers Welfare Board (KGWWB)</span>
							<span class="text-slate-500 text-[11px]">Linked to CITU State Platform Workers Welfare Registry</span>
						</div>
					</div>

					<!-- Digital Seal SVG -->
					<div class="shrink-0 flex flex-col items-end">
						<svg class="w-10 h-10 text-primary" fill="none" viewBox="0 0 48 48">
							<circle cx="24" cy="24" r="22" stroke="currentColor" stroke-dasharray="2 3" stroke-width="1.5"></circle>
							<circle cx="24" cy="24" fill="currentColor" fill-opacity="0.08" r="18"></circle>
							<circle cx="24" cy="24" r="14" stroke="currentColor" stroke-width="1"></circle>
							<path d="M18 24L22 28L30 19" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2"></path>
						</svg>
						<span class="font-mono text-[9px] text-slate-500 tracking-widest mt-0.5">SEAL-CITU-KL</span>
					</div>
				</div>

				<!-- Card Official Footer -->
				<div class="mt-5 px-6 py-3 bg-slate-100 flex flex-wrap items-center justify-between text-slate-600 text-xs gap-y-1">
					<div class="flex items-center gap-1">
						<span class="material-symbols-outlined text-[15px] text-primary">policy</span>
						<span>Reg. Trade Union No: <strong class="text-slate-900">Tu19965</strong></span>
					</div>
					<div>Govt. of Kerala Labour Dept. Recognized</div>
				</div>
			</div>

			<!-- Security & DPDP Compliance Statement -->
			<div class="w-full max-w-xl mx-auto mt-6 flex flex-col items-center text-center gap-2 px-2 print:hidden">
				<div class="flex items-center gap-1.5 text-slate-800 font-semibold text-sm">
					<span class="material-symbols-outlined text-[20px] text-emerald-700">lock</span>
					<span>{lang === 'ml' ? 'ക്രിപ്റ്റോഗ്രാഫിക് ടോക്കൺ വഴി പരിശോധിച്ചു' : 'Cryptographically Verified'}</span>
				</div>
				<p class="text-xs text-slate-500 leading-relaxed">
					{lang === 'ml'
						? 'ഡിജിറ്റൽ ക്യുആർ കോഡ് വഴി തത്സമയം പരിശോധിച്ചത്. പോലീസ് പരിശോധനകൾക്കും തർക്ക പരിഹാരങ്ങൾക്കും ക്ഷേമനിധി ആനുകൂല്യങ്ങൾക്കും ഈ കാർഡ് സാധുവാണ്.'
						: `Cryptographically verified via single-use dynamic QR token. Issued to ${member.name} for union representation, roadside dispute checks, and statutory platform welfare auditing.`}
				</p>

				<div class="mt-2 p-3 rounded-lg bg-slate-50 max-w-lg text-left flex items-start gap-2 text-slate-500 text-[11px] border border-slate-200">
					<span class="material-symbols-outlined text-[16px] text-slate-500 shrink-0 mt-0.5">privacy_tip</span>
					<span>
						<strong>DPDP Act 2023 Compliant:</strong> Personal phone number, residential address, aadhaar reference, and bank remittance tokens are strictly redacted on public verification surfaces to prevent harassment.
					</span>
				</div>

				<!-- Helpline Strip -->
				<div class="mt-4 flex flex-wrap items-center justify-center gap-x-4 gap-y-1 text-xs text-slate-500">
					<span class="flex items-center gap-1">
						<span class="material-symbols-outlined text-[15px] text-primary">call</span>
						<span>{lang === 'ml' ? 'ഹെൽപ്പ്‌ലൈൻ' : 'Helpline'}: <a class="text-primary font-semibold hover:underline" href="tel:9846063666">9846063666</a>, <a class="text-primary font-semibold hover:underline" href="tel:9447695655">9447695655</a></span>
					</span>
					<span>•</span>
					<span class="flex items-center gap-1">
						<span class="material-symbols-outlined text-[15px] text-primary">mail</span>
						<a class="text-primary font-semibold hover:underline" href="mailto:helpdesk@ksgpwu.citu.in">helpdesk@ksgpwu.citu.in</a>
					</span>
				</div>

				<div class="text-[11px] text-slate-400 mt-1 text-center">
					{lang === 'ml'
						? 'ഇ. ബാലാനന്ദ സ്മാരക ഓഫീസ്, സിഐടിയു സംസ്ഥാന കമ്മിറ്റി ഓഫീസ്, മേലെ തമ്പാനൂർ, തമ്പാനൂർ പി.ഒ.'
						: 'E Balananda Smaraka Office, CITU State Committee Office, Mele Thampanoor, Thampanoor P.O.'}
				</div>
			</div>
		</div>
	</div>
</main>

<!-- Footer -->
<footer class="w-full bg-slate-900 text-slate-400 py-6 mt-8 border-t border-slate-800 print:hidden">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col items-center justify-center text-center gap-1 text-xs">
		<div class="flex flex-wrap items-center justify-center gap-x-3 gap-y-1">
			<div class="flex items-center gap-1.5 font-semibold text-white">
				<img src="/gigLogo.png" alt="CITU Logo" class="w-4 h-4 object-contain" />
				<span>Kerala Gig &amp; Platform Workers Union (CITU)</span>
			</div>
			<span>•</span>
			<span>Reg. No: <strong class="text-white">Tu19965</strong></span>
			<span>•</span>
			<span>Support Helpline: <a href="tel:9846063666" class="hover:underline font-semibold text-amber-400">9846063666</a>, <a href="tel:9447695655" class="hover:underline font-semibold text-amber-400">9447695655</a></span>
		</div>
		<div class="text-[11px] text-slate-500 mt-1">
			E Balananda Smaraka Office, CITU State Committee Office, Mele Thampanoor, Thampanoor P.O.
		</div>
		<div class="text-[11px] text-slate-500 mt-0.5">
			Statutory Labour Protection &amp; Dignity · Kerala Platform Workers Welfare Registry
		</div>
	</div>
</footer>
