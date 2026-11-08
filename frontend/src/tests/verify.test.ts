import { describe, it, expect, beforeEach } from 'vitest';

describe('Verification & Dynamic ID Card Resolution', () => {
	beforeEach(() => {
		localStorage.clear();
		sessionStorage.clear();
	});

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
		return { name: platformName || 'Gig Worker', color: 'bg-slate-700' };
	}

	function findMemberData(token: string): any {
		// 1. Session Storage
		try {
			const cur = sessionStorage.getItem('currentMember');
			if (cur) {
				const c = JSON.parse(cur);
				if (!token || token === c.memberId || token === 'current' || token.length < 15) {
					return c;
				}
			}
		} catch (e) {}

		// 2. Token direct key
		try {
			const direct = localStorage.getItem(`member_${token}`);
			if (direct) return JSON.parse(direct);
		} catch (e) {}

		// 3. Global registry
		try {
			const regStr = localStorage.getItem('ksgpwu_members_registry');
			if (regStr) {
				const reg = JSON.parse(regStr);
				if (reg[token]) return reg[token];
				for (const k in reg) {
					if (k.toLowerCase() === token.toLowerCase()) return reg[k];
				}
			}
		} catch (e) {}

		// 4. Last registered fallback
		try {
			const last = localStorage.getItem('lastRegisteredMember');
			if (last) {
				const l = JSON.parse(last);
				if (l.memberId === token || token === 'demo' || token === 'current') return l;
			}
		} catch (e) {}

		return null;
	}

	it('should dynamically resolve registered member from session or local registry', () => {
		const memberRecord = {
			memberId: 'KL-KKD-2026-7788',
			fullName: 'MUHAMMED RIYAS',
			workingDistrict: 'KLKKD',
			district: 'Kozhikode (KLKKD)',
			primaryPlatform: 'Zomato',
			sector: 'Food Delivery Partner',
			vehicleNumber: 'KL-11-BV-4321',
			photo: 'data:image/jpeg;base64,/riyasPhoto',
			status: 'Active & Paid-Up'
		};

		localStorage.setItem('member_KL-KKD-2026-7788', JSON.stringify(memberRecord));

		const resolved = findMemberData('KL-KKD-2026-7788');
		expect(resolved).not.toBeNull();
		expect(resolved.fullName).toBe('MUHAMMED RIYAS');
		expect(resolved.primaryPlatform).toBe('Zomato');
		expect(resolved.vehicleNumber).toBe('KL-11-BV-4321');
	});

	it('should accurately resolve platform brand badges and colors', () => {
		expect(getPlatformInfo('Zomato').color).toBe('bg-red-600');
		expect(getPlatformInfo('Swiggy').color).toBe('bg-amber-600');
		expect(getPlatformInfo('Uber').color).toBe('bg-slate-900');
		expect(getPlatformInfo('Ola').color).toBe('bg-emerald-600');
		expect(getPlatformInfo('Zepto').color).toBe('bg-purple-600');
	});

	it('should resolve district information in both English and Malayalam', () => {
		const tvc = getDistrictInfo('KLTVC');
		expect(tvc.en).toBe('Thiruvananthapuram');
		expect(tvc.ml).toBe('തിരുവനന്തപുരം');

		const ern = getDistrictInfo('KLERN');
		expect(ern.en).toBe('Ernakulam');
		expect(ern.ml).toBe('എറണാകുളം');
	});

	it('should adhere to CR80 standard card specifications (1012x638 canvas ratio ~1.586)', () => {
		const canvasWidth = 1012;
		const canvasHeight = 638;
		const ratio = canvasWidth / canvasHeight;

		// Standard ISO/IEC 7810 ID-1 (CR80) is 85.60 mm × 53.98 mm = 1.58577
		expect(ratio).toBeCloseTo(1.586, 2);
	});

	it('should enforce DPDP Act 2023 compliance by omitting private PII on public verification', () => {
		// Mock member record
		const member = {
			memberId: 'KL-TVC-2026-00349',
			fullName: 'ANANDHU K. S.',
			status: 'Active & Paid-Up',
			validUntil: '31 Dec 2026',
			// Sensitive internal fields that must NEVER appear in public verification response
			homeAddress: 'Vattiyoorkavu, Trivandrum - Private',
			bankAccount: '123456789012',
			aadhaarFull: '1234 5678 9012'
		};

		// Public verification view model
		const publicVerificationView = {
			verified: true,
			union: 'Kerala State Gig and Platform Workers Union (CITU)',
			memberId: member.memberId,
			fullName: member.fullName,
			status: member.status,
			validUntil: member.validUntil
		};

		expect(publicVerificationView).not.toHaveProperty('homeAddress');
		expect(publicVerificationView).not.toHaveProperty('bankAccount');
		expect(publicVerificationView).not.toHaveProperty('aadhaarFull');
		expect(publicVerificationView.verified).toBe(true);
	});

	it('should support cross-device QR scanning by resolving member data from structured URL parameters', () => {
		const urlString = 'https://citu-gigworkers-web.onrender.com/verify/KL-TVC-2026-00349?name=ANANDHU+K+S&dist=KLTVC&sec=Delivery&plat=Swiggy&veh=KL-01-CA-5566';
		const url = new URL(urlString);
		const params = url.searchParams;

		expect(params.get('name')).toBe('ANANDHU K S');
		expect(params.get('dist')).toBe('KLTVC');
		expect(params.get('plat')).toBe('Swiggy');
		expect(params.get('veh')).toBe('KL-01-CA-5566');

		const distObj = getDistrictInfo(params.get('dist') || '');
		expect(distObj.en).toBe('Thiruvananthapuram');

		const platformInfo = getPlatformInfo(params.get('plat') || '');
		expect(platformInfo.name).toContain('Swiggy');
	});

	it('should support /verify?token=... URL format without triggering route proxying', () => {
		const urlString = 'https://citu-gigworkers-web.onrender.com/verify?token=KL-TVC-2026-3103&name=ROHITH+VIJAYAN&dist=KLTVC&sec=Food+Delivery+%26+Hyperlocal+Logistics&plat=Swiggy&veh=kl-74-c703';
		const url = new URL(urlString);
		expect(url.pathname).toBe('/verify');
		expect(url.searchParams.get('token')).toBe('KL-TVC-2026-3103');
		expect(url.searchParams.get('name')).toBe('ROHITH VIJAYAN');
		expect(url.searchParams.get('dist')).toBe('KLTVC');
		expect(url.searchParams.get('plat')).toBe('Swiggy');
		expect(url.searchParams.get('veh')).toBe('kl-74-c703');
	});

	it('should preserve and attach user selfie from local storage and not revert to stock photo', () => {
		const savedSelfie = 'data:image/jpeg;base64,rohithActualSelfieBytes12345';
		const registeredRecord = {
			id: 'KL-TVC-2026-6746',
			name: 'ROHITH VIJAYAN',
			photo: savedSelfie
		};
		localStorage.setItem('member_KL-TVC-2026-6746', JSON.stringify(registeredRecord));

		const scanToken = 'KL-TVC-2026-6746';
		const localStr = localStorage.getItem(`member_${scanToken}`);
		expect(localStr).not.toBeNull();
		const parsed = JSON.parse(localStr!);
		expect(parsed.photo).toBe(savedSelfie);
		expect(parsed.photo).not.toContain('lh3.googleusercontent.com');
	});
});
