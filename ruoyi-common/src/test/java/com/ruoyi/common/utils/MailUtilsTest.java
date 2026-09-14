package com.ruoyi.common.utils;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class MailUtilsTest
{
    @Test
    void formatFromHeaderUsesDisplayNameAndAddress()
    {
        assertEquals("Alchemy <alchemy@example.com>",
            MailUtils.formatFromHeader("alchemy@example.com", "Alchemy"));
    }

    @Test
    void resolveFromAddressPrefersConfiguredAlias()
    {
        assertEquals("alchemy@example.com",
            MailUtils.resolveFromAddress("alchemy@example.com", "smtp@example.com"));
    }

    @Test
    void resolveFromAddressFallsBackToSmtpUsername()
    {
        assertEquals("smtp@example.com", MailUtils.resolveFromAddress(null, "smtp@example.com"));
        assertEquals("smtp@example.com", MailUtils.resolveFromAddress("", "smtp@example.com"));
        assertEquals("smtp@example.com", MailUtils.resolveFromAddress("  ", "smtp@example.com"));
    }
}
