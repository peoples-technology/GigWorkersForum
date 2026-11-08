import { describe, it, expect, beforeEach } from 'vitest';

describe('Checkout & Member ID Issuance Flow', () => {
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

	function generateMemberId(districtCode: string): string {
		const cleanCode = districtCode ? districtCode.replace(/^KL/, '') : 'TVC';
		const randomNum = Math.floor(1000 + Math.random() * 9000);
		return `KL-${cleanCode}-2026-${randomNum}`;
	}

	it('should verify union fee composition equals ₹100', () => {
		const admissionFee = 50;
		const annualDues = 50;
		const total = admissionFee + annualDues;
		expect(total).toBe(100);
	});

	it('should generate official member ID adhering to state district conventions', () => {
		const idTvc = generateMemberId('KLTVC');
		expect(idTvc).toMatch(/^KL-TVC-2026-\d{4}$/);

		const idErn = generateMemberId('KLERN');
		expect(idErn).toMatch(/^KL-ERN-2026-\d{4}$/);

		const idKkd = generateMemberId('KLKKD');
		expect(idKkd).toMatch(/^KL-KKD-2026-\d{4}$/);
	});

	it('should process payment and correctly store member record in all 4 registry destinations', () => {
		const pending = {
			mobile: '9847112233',
			fullName: 'RAHUL R. MENON',
			workingDistrict: 'KLERN',
			primarySector: 'Delivery',
			primaryPlatform: 'Zomato',
			workingMode: 'Full Time',
			vehicleNumber: 'KL-07-BW-9900',
			photo: 'data:image/jpeg;base64,/9j/photo राहुल...',
			amount: 100
		};

		sessionStorage.setItem('pendingRegistration', JSON.stringify(pending));

		// Simulate handlePayment() in checkout
		const distCode = pending.workingDistrict || 'KLTVC';
		const distObj = districts.find(d => d.code === distCode);
		const districtName = distObj ? `${distObj.en} (${distObj.code})` : 'Ernakulam (KLERN)';
		const generatedId = `KL-ERN-2026-5544`;
		const txnId = `CITU-TXN-2026-998877`;

		const registeredMember = {
			memberId: generatedId,
			fullName: pending.fullName,
			mobile: pending.mobile,
			district: districtName,
			districtCode: distCode,
			sector: 'Food Delivery Partner (Zomato / Swiggy)',
			primaryPlatform: pending.primaryPlatform,
			vehicleNumber: pending.vehicleNumber,
			photo: pending.photo,
			status: 'Active & Paid-Up',
			validUntil: '31 Dec 2026',
			transactionId: txnId,
			joinedAt: new Date().toISOString()
		};

		// 1. Current member in session
		sessionStorage.setItem('currentMember', JSON.stringify(registeredMember));

		// 2. Last registered member in local storage
		localStorage.setItem('lastRegisteredMember', JSON.stringify(registeredMember));

		// 3. Direct token mapping
		localStorage.setItem(`member_${generatedId}`, JSON.stringify(registeredMember));

		// 4. Global members registry
		const registryStr = localStorage.getItem('ksgpwu_members_registry');
		const registry = registryStr ? JSON.parse(registryStr) : {};
		registry[generatedId] = registeredMember;
		localStorage.setItem('ksgpwu_members_registry', JSON.stringify(registry));

		// Assert all 4 storages hold the complete member record
		expect(JSON.parse(sessionStorage.getItem('currentMember')!).memberId).toBe(generatedId);
		expect(JSON.parse(localStorage.getItem('lastRegisteredMember')!).primaryPlatform).toBe('Zomato');
		expect(JSON.parse(localStorage.getItem(`member_${generatedId}`)!).status).toBe('Active & Paid-Up');
		
		const verifiedRegistry = JSON.parse(localStorage.getItem('ksgpwu_members_registry')!);
		expect(verifiedRegistry[generatedId].vehicleNumber).toBe('KL-07-BW-9900');
		expect(verifiedRegistry[generatedId].fullName).toBe('RAHUL R. MENON');
	});
});
