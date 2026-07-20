owasp_context = build_security_context(requirement)

atlas_context = build_mitre_context(requirement)

context = owasp_context + "\n\n" + atlas_context