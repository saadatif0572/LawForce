# LAWVERSE Corpus Coverage & Verification Report

**Generated:** 2026-08-21T09:24:07.856836+00:00  
**Total Verified PDF Documents:** 500  
**Integrity Status:** 100% Verified (0 Missing, 0 Corrupted, 0 Duplicate Checksums)

---

## 1. Statutory Allocation Breakdown

| Corpus Area | Target | Verified Actual | Status |
|---|---|---|---|
| Constitution & Constitutional Amendments | 30 | 30 | Complete |
| Core Federal Acts, Ordinances & Statutes | 180 | 180 | Complete |
| Federal Rules & Subordinate Legislation | 60 | 60 | Complete |
| Punjab Laws & Rules | 60 | 60 | Complete |
| Sindh Laws & Rules | 50 | 50 | Complete |
| Khyber Pakhtunkhwa Laws & Rules | 50 | 50 | Complete |
| Balochistan Laws & Rules | 40 | 40 | Complete |
| Supreme Court Landmark Judgments | 20 | 20 | Complete |
| High Court Reported Judgments | 10 | 10 | Complete |
| **Total** | **500** | **500** | **100% Delivered** |

---

## 2. Subject Matter Distribution

| Category | Document Count |
|---|---|
| Provincial Law | 182 |
| Administrative | 52 |
| Constitutional | 30 |
| Case Law | 30 |
| Criminal | 15 |
| Banking | 14 |
| Civil | 10 |
| Property | 8 |
| Health | 8 |
| Maritime | 8 |
| Family | 7 |
| Human Rights | 7 |
| Taxation | 6 |
| Energy | 6 |
| Judiciary | 5 |
| Local Government | 5 |
| Consumer | 5 |
| Commercial | 4 |
| Corporate | 4 |
| Media | 4 |
| Intellectual Property | 4 |
| Labour | 4 |
| Service Law | 4 |
| Commerce | 4 |
| Environmental | 3 |
| Trade | 3 |
| Education | 3 |
| Transport | 3 |
| Aviation | 3 |
| Profession | 3 |
| Agriculture | 3 |
| Environment | 3 |
| Cybercrime | 2 |
| Investigation | 2 |
| Customs | 2 |
| Governance | 2 |
| Investment | 2 |
| Industry | 2 |
| Citizenship | 2 |
| Immigration | 2 |
| Narcotics | 2 |
| Islamic | 2 |
| Finance | 2 |
| Infrastructure | 2 |
| Security | 2 |
| Water | 2 |
| Social Welfare | 2 |
| Evidence | 1 |
| Anti Corruption | 1 |
| Securities | 1 |
| Elections | 1 |
| Procurement | 1 |
| Insurance | 1 |
| Islamic Finance | 1 |
| Travel | 1 |
| Overseas Employment | 1 |
| Tenancy | 1 |
| Legal Profession | 1 |
| Telecom | 1 |
| Audit | 1 |
| Disaster Management | 1 |
| Postal | 1 |
| Standards | 1 |
| Business | 1 |
| Fintech | 1 |
| Women Rights | 1 |
| Police | 1 |

---

## 3. Official Source Provenance

Every document in the verified corpus is sourced from authorized Pakistani public registries:
- **Pakistan Code (Ministry of Law and Justice):** https://pakistancode.gov.pk
- **National Assembly of Pakistan:** https://na.gov.pk
- **Senate of Pakistan:** https://senate.gov.pk
- **Punjab Laws Online:** https://punjablaws.gov.pk
- **Sindh Code / Sindh Law Department:** https://www.sindhlaws.gov.pk
- **Khyber Pakhtunkhwa Code:** https://kpcode.kp.gov.pk
- **Balochistan Code:** https://balochistancode.gob.pk
- **Supreme Court of Pakistan:** https://www.supremecourt.gov.pk
- **Lahore High Court:** https://data.lhc.gov.pk
- **Islamabad High Court:** https://mis.ihc.gov.pk
- **Sindh High Court:** https://sindhhighcourt.gov.pk
- **Peshawar High Court:** https://peshawarhighcourt.gov.pk

---

## 4. Maintenance & Version Refresh Procedures

1. **Periodic Hash Checks:** Automated cron job checks upstream gazette RSS feeds and Ministry of Law bulletins for newly gazetted amendments.
2. **Version Stamping:** When a statutory amendment is enacted, a new document version is appended with `legal_status: amended` or `superseded` without altering the historical audit trail.
3. **Repeal Registry:** Superseded or repealed legislation (e.g. historical ordinances) is flagged as `legal_status: repealed` so the RAG assistant explicitly alerts users before referencing historical provisions.
