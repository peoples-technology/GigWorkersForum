import { writable } from 'svelte/store';

export type Language = 'ml' | 'en';

const initialLang: Language =
	typeof window !== 'undefined' && localStorage.getItem('citu_lang') === 'en' ? 'en' : 'ml';

export const currentLanguage = writable<Language>(initialLang);

export function setLanguage(lang: Language) {
	currentLanguage.set(lang);
	if (typeof window !== 'undefined') {
		localStorage.setItem('citu_lang', lang);
	}
}

export const translations = {
	ml: {
		unionTitle: 'കേരള സ്റ്റേറ്റ് ഗിഗ് & പ്ലാറ്റ്‌ഫോം വർക്കേഴ്സ് യൂണിയൻ (സി.ഐ.ടി.യു)',
		unionShort: 'സി.ഐ.ടി.യു ഗിഗ് വർക്കേഴ്സ് യൂണിയൻ',
		tagline: 'തൊഴിലാളി ഐക്യം സിന്ദാബാദ്! സാമൂഹിക സുരക്ഷ ഉറപ്പാക്കുക',
		step1: 'ഘട്ടം 1: ഫോൺ നമ്പർ പരിശോധന',
		step2: 'ഘട്ടം 2: വ്യക്തിഗത & തൊഴിൽ വിവരങ്ങൾ',
		step3: 'ഘട്ടം 3: തിരിച്ചറിയൽ രേഖ & സമ്മതം',
		step4: 'ഘട്ടം 4: ഡിജിറ്റൽ യൂണിയൻ കാർഡ്',
		mobileLabel: 'മൊബൈൽ നമ്പർ',
		mobilePlaceholder: '10 അക്ക മൊബൈൽ നമ്പർ നൽകുക',
		sendOtp: 'ഒ.ടി.പി അയക്കുക',
		otpLabel: 'ലഭിച്ച ഒ.ടി.പി നൽകുക',
		verifyOtp: 'പരിശോധിച്ച് തുടരുക',
		resendOtp: 'വീണ്ടും അയക്കുക',
		feeNotice: 'മെമ്പർഷിപ്പ് ഫീസ്: ₹160 (₹100 പ്രവേശന ഫീസ് + 6 മാസത്തെ വരിസംഖ്യ ₹60)',
		fullName: 'മുഴുവൻ പേര് (ആധാർ / ഡി.എൽ പ്രകാരം)',
		dob: 'ജനന തീയതി',
		ageValid: 'വയസ്സ് (അർഹതയുണ്ട്)',
		district: 'ജോലി ചെയ്യുന്ന ജില്ല',
		workingMode: 'തൊഴിൽ രീതി',
		fullTime: 'മുഴുവൻ സമയ',
		partTime: 'പാർട്ട് ടൈം',
		weekend: 'വാരാന്ത്യം',
		primaryPlatform: 'പ്രധാന പ്ലാറ്റ്‌ഫോം',
		vehicleType: 'വാഹന തരം',
		vehicleReg: 'വാഹന രജിസ്ട്രേഷൻ നമ്പർ',
		liveSelfie: 'തത്സമയ സെൽഫി ഫോട്ടോ',
		takeSelfie: 'സെൽഫി എടുക്കുക',
		idDocType: 'തിരിച്ചറിയൽ രേഖയുടെ തരം',
		idLast4: 'അവസാന 4 അക്കങ്ങൾ മാത്രം',
		dpdpNotice: 'DPDP ആക്ട് 2023 പ്രകാരം പൂർണ്ണ ആധാർ നമ്പർ ശേഖരിക്കുന്നതല്ല. സുരക്ഷിതത്വം ഉറപ്പ്.',
		consentStatement: 'ഞാൻ സി.ഐ.ടി.യു യൂണിയൻ ഭരണഘടനയും ചട്ടങ്ങളും പൂർണ്ണമായി അംഗീകരിക്കുന്നു.',
		payAndJoin: '₹160 അടച്ച് അംഗത്വം നേടുക',
		congratsComrade: 'സ്വാഗതം സഖാവേ! നിങ്ങളുടെ അംഗത്വം സജീവമായി.',
		membershipNo: 'മെമ്പർഷിപ്പ് നമ്പർ',
		downloadCardPdf: 'കാർഡ് ഡൗൺലോഡ് (PDF)',
		joinWhatsApp: 'ജില്ലാ വാട്സ്ആപ്പ് ഗ്രൂപ്പിൽ ചേരുക',
		grievanceHelp: 'തൊഴിലാളി സഹായ കേന്ദ്രം & നിയമ സഹായം',
		viewReceipt: 'രസീത് ഡൗൺലോഡ്'
	},
	en: {
		unionTitle: 'Kerala State Gig & Platform Workers Union (CITU)',
		unionShort: 'CITU Gig Workers Union',
		tagline: 'Workers United! Ensuring Social Security & Dignity of Labour',
		step1: 'Step 1: Mobile Phone Verification',
		step2: 'Step 2: Personal & Work Profile',
		step3: 'Step 3: Identity Verification & Consent',
		step4: 'Step 4: Digital Membership Card',
		mobileLabel: 'Mobile Number',
		mobilePlaceholder: 'Enter 10-digit mobile number',
		sendOtp: 'Send OTP',
		otpLabel: 'Enter 6-digit OTP',
		verifyOtp: 'Verify & Continue',
		resendOtp: 'Resend OTP',
		feeNotice: 'Statutory Fee: ₹160 (₹100 Registration + 6 Months Subscription ₹60)',
		fullName: 'Full Name (as on Aadhaar / DL)',
		dob: 'Date of Birth',
		ageValid: 'Yrs (Eligible)',
		district: 'Working District',
		workingMode: 'Working Mode',
		fullTime: 'Full-Time',
		partTime: 'Part-Time',
		weekend: 'Weekend',
		primaryPlatform: 'Primary Platform',
		vehicleType: 'Vehicle Type',
		vehicleReg: 'Vehicle Registration No',
		liveSelfie: 'Live Camera Selfie',
		takeSelfie: 'Capture Selfie',
		idDocType: 'ID Document Type',
		idLast4: 'Last 4 Digits Only',
		dpdpNotice: 'Protected under DPDP Act 2023. Full Aadhaar is never stored.',
		consentStatement: 'I hereby agree to abide by the CITU constitution, bylaws, and union decisions.',
		payAndJoin: 'Pay ₹160 & Activate Membership',
		congratsComrade: 'Welcome Comrade! Your membership is active.',
		membershipNo: 'Membership Number',
		downloadCardPdf: 'Download Card (PDF)',
		joinWhatsApp: 'Join District WhatsApp Group',
		grievanceHelp: 'Worker Helpdesk & Legal Cell',
		viewReceipt: 'Download Receipt'
	}
};
