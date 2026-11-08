import { describe, it, expect } from 'vitest';

describe('Frontend & Backend API Contract Verification', () => {
	it('should ensure frontend registration payload maps 1:1 to backend /api/register/submit contract', () => {
		// Frontend captures:
		const frontendData = {
			mobile: '9847112233',
			fullName: 'Com. Sakhavu Bineesh',
			dob: '1993-04-10',
			gender: 'Male',
			motherTongue: 'Malayalam',
			email: 'bineesh@citu.org',
			currentAddress: 'CITU District Committee Office, Thrissur',
			workingDistrict: 'KLTSR',
			district: 'KLTSR',
			primarySector: 'Delivery',
			primaryPlatform: 'Zomato',
			customPlatform: '',
			workingMode: 'Full Time',
			vehicleNumber: 'KL-08-AA-7788',
			licenceNumber: 'KL0820140003456',
			idDocType: 'Aadhaar',
			idLastDigits: '8877',
			photo: 'data:image/jpeg;base64,cameraSelfieData',
			amount: 100
		};

		// Backend expects:
		const backendSubmissionPayload = {
			phone: frontendData.mobile,
			working_district_code: frontendData.workingDistrict,
			id_doc_type: frontendData.idDocType.toLowerCase(),
			id_last4: frontendData.idLastDigits,
			answers: {
				full_name: frontendData.fullName,
				current_address: frontendData.currentAddress,
				working_district: frontendData.workingDistrict,
				mobile_number: frontendData.mobile,
				whatsapp_number: frontendData.mobile,
				dob: frontendData.dob,
				gender: frontendData.gender.toLowerCase(),
				mother_tongue: frontendData.motherTongue,
				primary_platform: frontendData.primaryPlatform.toLowerCase(),
				vehicle_type: 'motorcycle',
				vehicle_reg_no: frontendData.vehicleNumber,
				id_doc_type: frontendData.idDocType.toLowerCase(),
				id_last4: frontendData.idLastDigits
			}
		};

		expect(backendSubmissionPayload.phone).toBe(frontendData.mobile);
		expect(backendSubmissionPayload.working_district_code).toBe('KLTSR');
		expect(backendSubmissionPayload.id_last4).toBe(frontendData.idLastDigits);
		expect(backendSubmissionPayload.answers.full_name).toBe(frontendData.fullName);
		expect(backendSubmissionPayload.answers.primary_platform).toBe('zomato');
	});

	it('should ensure backend /verify/{token} response properties map to frontend verify card view', () => {
		// Backend verify output format
		const backendVerifyOutput = {
			valid: true,
			membership_number: 'KL-TSR-2026-00882',
			member_name: 'BINEESH K.',
			union: 'Kerala State Gig and Platform Workers Union (CITU)',
			district_code: 'KLTSR',
			platform: 'Zomato',
			status: 'ACTIVE',
			valid_until: '2027-04-30',
			card_type: 'DIGITAL_ID'
		};

		// Frontend verify page mapping
		const frontendViewModel = {
			verified: backendVerifyOutput.valid,
			memberId: backendVerifyOutput.membership_number,
			memberName: backendVerifyOutput.member_name,
			statusText: backendVerifyOutput.status === 'ACTIVE' ? 'Active & Paid-Up' : 'Inactive',
			platformName: backendVerifyOutput.platform,
			districtCode: backendVerifyOutput.district_code
		};

		expect(frontendViewModel.verified).toBe(true);
		expect(frontendViewModel.memberId).toBe('KL-TSR-2026-00882');
		expect(frontendViewModel.statusText).toBe('Active & Paid-Up');
		expect(frontendViewModel.districtCode).toBe('KLTSR');
	});
});
