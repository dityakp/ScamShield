"""
Download multiple public spam/scam/phishing datasets from the web and build
a single comprehensive training CSV: app/ml/data/sample_scams.csv

Sources (all fetched automatically):
  1. UCI SMS Spam Collection          – 5,574 SMS (GitHub mirror)
  2. Kaggle SMS Spam Collection       – ~5,572 SMS (GitHub mirror, slightly different encoding)
  3. Combined Smishing Dataset        – ~5,000+ labeled smishing SMS (GitHub)
  4. Hand-crafted Indian scam + safe  – ~240 messages

Usage:
    cd backend
    python -m app.ml.build_dataset
"""

import csv
import urllib.request
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
OUTPUT_PATH = DATA_DIR / "sample_scams.csv"

HEADERS = {"User-Agent": "ScamShield/1.0"}


def _fetch(url: str, timeout: int = 30) -> str:
    """Download a URL and return its content as a string."""
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


# ── Source 1: UCI SMS Spam Collection (TSV) ───────────────────
UCI_URL = "https://raw.githubusercontent.com/justmarkham/pycon-2016-tutorial/master/data/sms.tsv"


def download_uci_sms() -> list:
    print("[1/4] Downloading UCI SMS Spam Collection...")
    try:
        raw = _fetch(UCI_URL)
    except Exception as e:
        print(f"  ⚠ Failed: {e}")
        return []
    rows = []
    for line in raw.strip().split("\n"):
        parts = line.split("\t", 1)
        if len(parts) != 2:
            continue
        lbl, text = parts[0].strip(), parts[1].strip()
        if lbl == "label":
            continue
        label = 1 if lbl.lower() == "spam" else 0
        if text:
            rows.append((text, label))
    print(f"  ✓ {len(rows)} messages  (spam={sum(1 for _,l in rows if l==1)})")
    return rows


# ── Source 2: Kaggle SMS Spam Collection (CSV) ────────────────
KAGGLE_URL = "https://raw.githubusercontent.com/mohitgupta-1O1/Kaggle-SMS-Spam-Collection-Dataset-/master/spam.csv"


def download_kaggle_spam() -> list:
    print("[2/4] Downloading Kaggle SMS Spam Collection...")
    try:
        raw = _fetch(KAGGLE_URL)
    except Exception as e:
        print(f"  ⚠ Failed: {e}")
        return []
    rows = []
    import io
    reader = csv.reader(io.StringIO(raw))
    header = next(reader, None)
    for row_data in reader:
        if len(row_data) < 2:
            continue
        lbl = row_data[0].strip()
        text = row_data[1].strip()
        if lbl in ("v1", "label"):
            continue
        label = 1 if lbl.lower() == "spam" else 0
        if text and len(text) > 5:
            rows.append((text, label))
    print(f"  ✓ {len(rows)} messages  (spam={sum(1 for _,l in rows if l==1)})")
    return rows


# ── Source 3: Combined Labeled Smishing Dataset ───────────────
SMISHING_URL = "https://raw.githubusercontent.com/shaghayegh-hp/Smishing_Dataset/main/Combined-Labeled-Dataset.csv"


def download_smishing() -> list:
    print("[3/4] Downloading Combined Smishing Dataset...")
    try:
        raw = _fetch(SMISHING_URL)
    except Exception as e:
        print(f"  ⚠ Failed: {e}")
        return []
    rows = []
    import io
    reader = csv.DictReader(io.StringIO(raw))
    for row_data in reader:
        text = ""
        # Try common column names
        for col in ("message", "text", "sms", "Message", "Text", "SMS"):
            if col in row_data and row_data[col]:
                text = row_data[col].strip()
                break
        if not text:
            # Try first text-like column
            for k, v in row_data.items():
                if v and len(str(v)) > 20:
                    text = str(v).strip()
                    break
        if not text or len(text) < 5:
            continue

        # Determine label: prefer smishing label, then spam label
        label = 0
        for col in ("smishing label", "smishing_label", "label", "spam label", "spam_label"):
            if col in row_data:
                try:
                    val = int(row_data[col])
                    if val == 1:
                        label = 1
                    break
                except ValueError:
                    continue
        rows.append((text, label))
    print(f"  ✓ {len(rows)} messages  (smishing/spam={sum(1 for _,l in rows if l==1)})")
    return rows


# ── Source 4: Hand-crafted Indian scam + safe messages ────────
HANDCRAFTED_DATA = [
    # ═══ SCAM / PHISHING (label=1) ═══
    # UPI / Banking
    ("Your bank account will be suspended in 24 hours. Click https://secure-verification-update.com to update your KYC immediately.", 1),
    ("Dear customer, your KYC is pending. Verify now to avoid account suspension: http://kyc-update-bank.com", 1),
    ("URGENT: Your UPI account has been compromised. Share your OTP immediately to secure it.", 1),
    ("Your SBI account has been temporarily blocked due to unusual activity. Verify your identity at http://sbi-secure-verify.com", 1),
    ("ICICI Bank Alert: Your account will be deactivated in 24 hours. Update KYC now: http://icici-kyc-update.in", 1),
    ("Your PhonePe account is under review. Complete verification within 2 hours or lose access: http://phonepe-verify.co", 1),
    ("Google Pay: Suspicious transaction of ₹9,999 detected. If this wasn't you, click here: http://gpay-secure.online", 1),
    ("RBI has mandated linking your Aadhaar with all bank accounts by March 31. Update now: http://rbi-aadhaar-link.in", 1),
    ("HDFC Life Insurance: You are eligible for a free policy worth ₹10 lakhs. Claim before midnight: http://hdfc-free-policy.co", 1),
    ("Paytm: Your wallet has been credited with ₹2,000 cashback. Transfer to bank: http://paytm-cashback-claim.in", 1),
    ("Axis Bank: Your debit card PIN has expired. Update here: http://axis-pin-update.in", 1),
    ("PNB Alert: ₹49,999 debited from your account. If not you, call helpline +91-8765432100 immediately.", 1),
    ("Your Kotak Mahindra account has new login from unknown device. If not you, click: http://kotak-secure.in", 1),
    ("NPCI Alert: Your UPI ID is being used on another device. Verify immediately: http://npci-verify.in", 1),
    ("Dear user, ₹10,000 credited to your account by mistake. Return via UPI to avoid legal action.", 1),
    ("Your SBI YONO app session has expired. Re-login at http://yono-sbi-login.co to continue banking.", 1),
    ("Bank of Baroda: Your internet banking will be blocked. Verify Aadhaar: http://bob-verify.online", 1),
    ("IDFC First Bank: Complete video KYC within 24 hours or your account will be frozen. Link: http://idfc-vkyc.site", 1),
    ("Your Bajaj Finance EMI payment has bounced. Pay immediately to avoid CIBIL impact: http://bajaj-pay.co", 1),
    ("Federal Bank Security: Unauthorized access to your account detected. Secure now: http://fed-bank-secure.in", 1),
    # OTP fraud
    ("Hi sir, I am from customer support. Please share your OTP to resolve your complaint.", 1),
    ("Your OTP for ₹25,000 transfer is 482931. If you did not initiate, share OTP to cancel.", 1),
    ("Amazon delivery: Your package is on hold. Share OTP 739281 to confirm delivery address.", 1),
    ("Flipkart order update: Enter OTP 856321 at http://flipkart-confirm.shop to receive your refund.", 1),
    ("Your Paytm KYC OTP is 912345. Share this with our executive on call to complete verification.", 1),
    ("SBI: Your OTP for password reset is 123456. Our agent will call you to complete the process.", 1),
    ("Vodafone: Your SIM reactivation OTP is 674523. Share with our store to avoid disconnection.", 1),
    ("IRCTC: Your booking OTP is 456789. Share with our agent to confirm your tatkal ticket.", 1),
    # Lottery / prize
    ("Congratulations! You have won a lottery worth ₹50,00,000. Click here to claim your prize now.", 1),
    ("You have been selected as a winner of our annual draw. Send your OTP to receive the prize money.", 1),
    ("FREE iPhone 15! You are today's lucky winner. Claim your gift at http://free-iphone.win", 1),
    ("Reliance Jio Lucky Draw: Your number won ₹25,00,000! Processing fee ₹999 only.", 1),
    ("WhatsApp Anniversary! You've been selected from millions. Win iPhone 16. Click: http://whatsapp-prize.win", 1),
    ("Dear Airtel user, you won a Samsung Galaxy S25 in our lucky draw! Claim: http://airtel-winner.shop", 1),
    ("Congratulations! Your email has been selected by UN Lottery Program. Claim $1M at http://un-lottery.org", 1),
    ("You have received ₹15,000 cashback! Tap this link to transfer to your bank account.", 1),
    ("KBC Lottery: You won ₹1 Crore! Call +91-9876543210 and provide your bank details to claim.", 1),
    ("Dear Vodafone user, your mobile number has won lucky draw! Transfer fee ₹999 to claim ₹10 lakh prize.", 1),
    ("Flipkart Big Billion Day Special: You won a MacBook Pro! Claim at http://flipkart-winner.shop", 1),
    ("BSNL Lucky Customer: You won ₹5,00,000! Pay processing fee of ₹500 to receive.", 1),
    ("Google Anniversary Lottery: Your Gmail has won $500,000. Reply with name and bank details.", 1),
    # Investment / crypto
    ("Get guaranteed 200% return on your investment in just 30 days! Join now: http://invest-quick.com", 1),
    ("Bitcoin is going to $500K! Invest now and get 10x returns guaranteed. Limited spots: http://btc-millionaire.net", 1),
    ("Join our exclusive forex trading group. 95% win rate. Free signals. WhatsApp: +91-8765432100", 1),
    ("Crypto airdrop! Claim 0.5 ETH worth ₹80,000 free. Connect wallet: http://eth-airdrop.finance", 1),
    ("Double your money in 48 hours with our AI trading bot. Minimum ₹5,000. Guaranteed returns.", 1),
    ("Earn ₹50,000 daily from home! No investment required. Join our WhatsApp group now.", 1),
    ("Investment opportunity: Put ₹10,000 and get ₹1,00,000 in 7 days. 100% guaranteed.", 1),
    ("Join our premium stock tips WhatsApp group. ₹10K to ₹1L in 30 days. SEBI registered.", 1),
    ("MLM opportunity! Recruit 5 members and earn ₹50,000 monthly. No product selling required.", 1),
    ("Binary options trading: 90% profit in 60 seconds. Start with just $10: http://binary-profit.net", 1),
    ("Gold investment scheme: Buy digital gold at 20% discount. Limited time: http://gold-discount.co", 1),
    ("Mutual fund guaranteed returns: 50% in 6 months. No risk. Register: http://mf-guaranteed.in", 1),
    # Job scams
    ("Hiring now! Work from home data entry job. Earn ₹30,000/month. No experience. WhatsApp: +91-9876543210", 1),
    ("Amazon is hiring part-time workers. ₹500/hour guaranteed. Apply now: http://amazon-hiring.click", 1),
    ("You have been selected for Google internship. Registration fee ₹2,000. Pay: http://google-intern.site", 1),
    ("Flipkart hiring delivery partners. Earn ₹50,000/month. No interview. Register: http://flipkart-jobs.online", 1),
    ("Work from home! Rate products on Amazon and earn ₹5,000 daily. Telegram: @EasyEarnings", 1),
    ("Part time job! Earn ₹5000-₹10000 daily by liking YouTube videos. Contact now.", 1),
    ("TCS Walk-in Interview: Freshers salary ₹45,000/month. Registration fee ₹1,500.", 1),
    ("Infosys is hiring! Work from home. ₹60,000/month. Pay ₹3,000 registration: http://infosys-wfh.site", 1),
    ("UPSC coaching free! Government job guaranteed. Just pay ₹2,000 registration.", 1),
    ("International job offer! Earn $5,000/month in Dubai. Visa free. Pay processing fee: ₹15,000", 1),
    ("Netflix hiring content reviewers. Work from home. ₹800/hour. Apply: http://netflix-jobs.click", 1),
    ("Earn by watching ads! ₹500 per ad. Download app: http://ad-earn.com.", 1),
    # Tech support / account
    ("ALERT: Suspicious login detected on your account. Click here immediately to reset your password.", 1),
    ("Microsoft Alert: Your Windows license has expired. Reactivate now: http://ms-reactivate.co", 1),
    ("Apple ID: Suspicious sign-in from Russia. Verify: http://apple-verify.click", 1),
    ("Your antivirus subscription has expired. Computer at risk! Renew: http://norton-renew.site", 1),
    ("Your phone has a virus! Download this security app: http://phone-security.app", 1),
    ("WARNING: Someone tried to access your Instagram. Verify: http://insta-verify.co", 1),
    ("IMPORTANT: Your Google account has been hacked. Reset: http://google-secure.click", 1),
    ("Your WhatsApp will be deleted in 48 hours. Verify: http://whatsapp-verify.site", 1),
    ("Your Netflix subscription has expired. Update payment: http://netflix-renew.co", 1),
    ("Facebook Security: Your account will be disabled. Confirm: http://fb-confirm.site", 1),
    ("iCloud storage full! Photos will be deleted. Upgrade: http://icloud-upgrade.click", 1),
    ("Twitter/X account suspended. Appeal within 24 hours: http://x-appeal.site", 1),
    ("Your Telegram account is at risk. Enable security: http://telegram-security.co", 1),
    # Government / identity
    ("Your PAN card linked to suspicious activity. Verify: http://pan-verify.in", 1),
    ("Income Tax Department: Pending refund of ₹15,000. Verify PAN: http://itr-refund.gov.in.click", 1),
    ("Police notice: Your mobile used in cybercrime. Call +91-9988776655 immediately.", 1),
    ("Your Aadhaar has been used for illegal activity. Verify: http://aadhaar-check.site", 1),
    ("Government giving ₹6,000 under PM scheme. Register with Aadhaar: http://pm-yojana.click", 1),
    ("Police cybercrime notice: Bank account under investigation. Transfer funds to safe account.", 1),
    ("Your DigiLocker compromised. Reset password: http://digilocker-reset.site", 1),
    ("EPFO Alert: PF withdrawal request rejected. Update KYC: http://epfo-kyc.in", 1),
    ("Passport office: Application rejected. Reapply: http://passport-reapply.site", 1),
    ("GST Notice: Tax evasion detected. Pay penalty ₹50,000 within 24 hours.", 1),
    ("RTO Alert: Driving license suspended. Pay fine: http://rto-fine.co", 1),
    ("Election Commission: Voter ID invalid. Update: http://eci-update.in before elections.", 1),
    # E-commerce / delivery
    ("Your Amazon order #A123 cancelled. Rebook: http://amazon-rebook.shop", 1),
    ("Customs: Amazon package held. Pay ₹499 clearance: http://customs-clearance.in", 1),
    ("IRCTC refund of ₹1,250 pending. Claim: http://irctc-refund.online", 1),
    ("Electricity bill overdue. Pay now to avoid disconnection: http://bill-pay-urgent.com", 1),
    ("Courier package held at customs. Pay ₹299: http://customs-pay.online", 1),
    ("Amazon Prime free for 1 year! Activate: http://amazon-prime-free.click", 1),
    ("Zomato/Swiggy refund of ₹500 ready. Click: http://food-refund.site", 1),
    ("Flipkart: Order cancelled due to payment issue. Re-pay: http://flipkart-repay.shop", 1),
    ("Meesho order undelivered. Update address: http://meesho-refund.site", 1),
    ("DTDC: Parcel delivery failed. Reschedule: http://dtdc-reschedule.in. Pay ₹99.", 1),
    ("BlueDart: Pay ₹199 customs duty: http://bluedart-duty.co", 1),
    # Romance / social
    ("Hi dear, I saw your profile. I'm a UN doctor in Syria. Send your number.", 1),
    ("Wealthy widow needs help to transfer $5M. You get 30% commission. Reply.", 1),
    ("Hey beautiful, found your number online. US army officer. Can I send a gift?", 1),
    ("Stuck abroad, need ₹20,000 for flight. Will return double tomorrow.", 1),
    # Misc scam
    ("Your Jio SIM deactivated in 24 hours. Recharge: http://jio-recharge.online", 1),
    ("Paytm KYC expiring today. Update: http://paytm-kyc.online", 1),
    ("CIBIL score dropped to 300. Check free: http://cibil-check-free.in", 1),
    ("RBI Notice: All bank accounts frozen. Update KYC: http://rbi-kyc.gov.in.click", 1),
    ("Flipkart gift voucher ₹5,000. Claim: http://reliance-gift.shop", 1),
    ("Earn ₹500 per survey. Register: http://survey-earn.com", 1),
    ("Task-based earning: Like, share, review products. Earn ₹800-₹2000/day!", 1),
    ("Ola/Uber account suspended. Reactivate: http://ride-verify.app", 1),
    ("Free COVID-19 booster dose. Register: http://covid-free-dose.in", 1),
    ("LIC policy lapsed. Pay revival charges: http://lic-revival.co", 1),
    ("BSNL broadband disconnection notice. Pay ₹2,500: http://bsnl-pay.online", 1),
    ("iPhone 15 at ₹9,999 only! Limited stock: http://iphone-deal.shop", 1),
    ("Car insurance expired! Renew 50% off: http://car-insurance-renew.in", 1),
    ("Free health insurance! Government scheme: http://health-scheme.in", 1),
    ("Gas connection subsidy ₹800 pending. Claim: http://lpg-subsidy.in", 1),
    ("Win a Royal Enfield Bullet! Answer 3 questions: http://re-quiz.co", 1),
    ("Email storage 99% full. Upgrade free: http://email-storage.click", 1),

    # ═══ SAFE / LEGITIMATE (label=0) ═══
    ("Hi, meeting confirmed for 3 PM tomorrow at Conference Room B.", 0),
    ("Hey, can we reschedule lunch to Thursday? Something came up.", 0),
    ("Happy birthday! Wishing you a wonderful year ahead. 🎂", 0),
    ("Are you coming to the hackathon this weekend? 9 AM Saturday.", 0),
    ("Code review for sprint 23 complete. All PRs merged.", 0),
    ("Happy Holi! Wishing you and your family a colorful celebration! 🎨", 0),
    ("Team lunch at 1 PM today at Punjabi Dhaba. Don't forget!", 0),
    ("Free for a call at 4 PM? Need to discuss the project timeline.", 0),
    ("Thanks for the gift! Lovely surprise. Let's catch up weekend.", 0),
    ("Pick up groceries on your way home? Milk, bread, and eggs.", 0),
    ("Congratulations on your promotion! Well deserved.", 0),
    ("Movie tonight? Pushpa 2 at Inox 7:30 PM. Get tickets?", 0),
    ("Safe travels! Let me know when you reach Bangalore.", 0),
    ("Mom's birthday next week. Plan a surprise dinner?", 0),
    ("Can you send notes from today's lecture? Missed last 30 min.", 0),
    ("Your order #12345 shipped. Arriving Friday.", 0),
    ("Amazon order delivered. Contact customer service if not received.", 0),
    ("Amazon return for 'Boat Earphones' accepted. Refund in 5-7 days.", 0),
    ("Flipkart: 'Noise Smartwatch' dispatched. On its way.", 0),
    ("Swiggy order from Dominos picked up. ETA: 20 minutes.", 0),
    ("Zomato: Rate your order from Pizza Hut!", 0),
    ("Myntra order (Levi's Jeans) shipped. Track at myntra.com/orders.", 0),
    ("LaundryMate order ready for pickup at Store #42, Sector 21.", 0),
    ("BigBasket: Grocery delivery tomorrow 10 AM - 12 PM.", 0),
    ("Dunzo order from Medical Store picked up. Arriving 15 min.", 0),
    ("Meesho order shipped! Track: meesho.com/track/MS123456", 0),
    ("Monthly bank statement for Feb available in net banking.", 0),
    ("HDFC FD ₹1,00,000 matured. Interest ₹7,250 credited.", 0),
    ("HDFC EMI ₹8,500 debited from account ending 4321. Balance: ₹45,230.", 0),
    ("SIP ₹5,000 in Axis Bluechip Fund debited for March.", 0),
    ("OTP for SBI net banking: 482931. Valid 10 min. Do not share.", 0),
    ("Rent ₹15,000 received via UPI. Transaction: UPI123456789.", 0),
    ("PhonePe ₹200 to Chai Point successful. Balance: ₹3,450.", 0),
    ("Zerodha holdings updated. Check portfolio in Kite app.", 0),
    ("ICICI credit card statement ready. Due: ₹12,500 by Mar 15.", 0),
    ("Kotak: Salary ₹55,000 credited. Balance: ₹1,23,450.", 0),
    ("SBI home loan EMI ₹22,500 auto-debited. Next: April 5.", 0),
    ("Paytm ₹500 cashback credited to wallet. No action needed.", 0),
    ("CIBIL score this month: 785. No significant changes.", 0),
    ("LIC premium reminder Policy 123456789. Due: ₹12,500 by Mar 20.", 0),
    ("Quarterly sales report attached. Review before Monday.", 0),
    ("Standup moved to 11 AM. Join usual Zoom link.", 0),
    ("Submit timesheet by end of day Friday.", 0),
    ("Sprint planning notes shared on Confluence.", 0),
    ("Follow up on last week's partnership proposal email.", 0),
    ("Stand-up cancelled today. Most team members on leave.", 0),
    ("Project deadline extended to March 28. Plan accordingly.", 0),
    ("Decided to use PostgreSQL for DB and FastAPI for backend.", 0),
    ("Finished presentation slides. Let me know about changes.", 0),
    ("Auth module code review done. Comments on GitHub.", 0),
    ("Appraisal meeting March 20 at 3 PM with your manager.", 0),
    ("New WiFi password: ScamShield@2026. Update devices.", 0),
    ("Library book 'Clean Code' due March 10. Return or renew.", 0),
    ("Coursera ML Specialization certificate ready to download.", 0),
    ("JEE Main admit card available at jeemain.nta.nic.in.", 0),
    ("TechFest 2026 registrations open. Register by March 20.", 0),
    ("NEET scorecard available at neet.nta.nic.in. All the best!", 0),
    ("Semester 6 results declared. Check university.ac.in.", 0),
    ("Parent-teacher meeting March 12 at 11 AM, Room 204.", 0),
    ("Assignment deadline extended to March 22. Submit via Classroom.", 0),
    ("IRCTC tatkal PNR 2341567890 confirmed. Rajdhani, Coach B3, Seat 42.", 0),
    ("Train PNR confirmed. Howrah Junction. Coach S5, Berth 32.", 0),
    ("Uber Andheri to Bandra ₹250. Receipt emailed.", 0),
    ("Ola Prime from Airport to MG Road confirmed. ETA: 5 min.", 0),
    ("IndiGo 6E-2345: Web check-in open. Seat 14A confirmed.", 0),
    ("GitHub PR #234 approved and merged into main.", 0),
    ("VS Code 1.96 available. Update for latest features.", 0),
    ("NPM express@5.0.0 released. Check changelog.", 0),
    ("NPM audit: 0 vulnerabilities. All deps up to date.", 0),
    ("GitHub Actions CI/CD completed in 2m 34s.", 0),
    ("Docker image push successful. scamshield/backend:latest.", 0),
    ("Vercel deployment successful. Live at scamshield.vercel.app.", 0),
    ("Electricity bill ₹1,450 for Feb generated. Due: March 15.", 0),
    ("Internet plan renewed. Next billing: April 1, 2026.", 0),
    ("LIC premium ₹12,500 due March 20. Pay via net banking.", 0),
    ("Airtel postpaid ₹799 for March. Due: April 10.", 0),
    ("Airtel prepaid ₹599 recharged. Validity: 56 days.", 0),
    ("LPG gas cylinder booking confirmed. Delivery in 3 days.", 0),
    ("Car insurance renewal due April 15. Review options.", 0),
    ("BSNL broadband: 180 GB of 300 GB used. No action needed.", 0),
    ("Tata Power bill ₹2,100 for Feb-Mar. Due: March 25.", 0),
    ("Jio Fiber ₹999 renewed. Speed: 150 Mbps.", 0),
    ("Dentist appointment March 15 at 10 AM.", 0),
    ("Blood test reports ready on Practo app.", 0),
    ("Apollo Pharmacy: Metformin 500mg refill ready for pickup.", 0),
    ("Passport application updated. Track at passportindia.gov.in.", 0),
    ("Submit income tax return before July 31.", 0),
    ("Voter ID dispatch confirmed. Delivery: 15 working days.", 0),
    ("Spotify Wrapped 2025 ready! See top artists in app.", 0),
    ("Gym membership expires March 31. Visit front desk to renew.", 0),
    ("Weather tomorrow: partly cloudy, high 28°C. Carry umbrella.", 0),
    ("Heavy rainfall expected in Kolkata tomorrow. Plan accordingly.", 0),
    ("BookMyShow: 'Pushpa 2' confirmed. Screen 3, J12-J14.", 0),
    ("Hotstar: 'Panchayat Season 4' now streaming!", 0),
    ("Gym membership auto-renewed 3 months. ₹4,500 charged.", 0),
]


def build_dataset():
    """Merge all sources into a single sample_scams.csv."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    all_rows = []

    # Source 1
    all_rows.extend(download_uci_sms())
    # Source 2
    all_rows.extend(download_kaggle_spam())
    # Source 3
    all_rows.extend(download_smishing())
    # Source 4
    print(f"[4/4] Adding {len(HANDCRAFTED_DATA)} hand-crafted samples...")
    all_rows.extend(HANDCRAFTED_DATA)

    # Deduplicate
    seen = set()
    unique = []
    for text, label in all_rows:
        key = text.strip().lower()
        if key not in seen and len(key) > 5:
            seen.add(key)
            unique.append((text.strip(), label))

    scam = sum(1 for _, l in unique if l == 1)
    safe = sum(1 for _, l in unique if l == 0)

    print(f"\n── Final Dataset ───────────────────────────")
    print(f"  Total unique samples:  {len(unique)}")
    print(f"  Scam/Spam (label=1):   {scam}")
    print(f"  Safe/Ham  (label=0):   {safe}")

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "label"])
        for text, label in unique:
            writer.writerow([text, label])

    print(f"\n  ✓ Saved to {OUTPUT_PATH}")

    # Clean up old training_data.csv if it exists
    old = DATA_DIR / "training_data.csv"
    if old.exists():
        old.unlink()
        print(f"  ✓ Removed old {old.name}")

    return OUTPUT_PATH


if __name__ == "__main__":
    build_dataset()
