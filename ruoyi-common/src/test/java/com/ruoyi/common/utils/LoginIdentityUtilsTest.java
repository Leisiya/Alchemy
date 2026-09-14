package com.ruoyi.common.utils;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;

class LoginIdentityUtilsTest
{
    @Test
    void emailLongerThanUsernameMaxIsValid()
    {
        assertTrue(LoginIdentityUtils.isLoginIdLengthValid("zhifanzhan3@gmail.com"));
    }

    @Test
    void emailAtMaxLengthIsValid()
    {
        String email50 = "a" + "x".repeat(44) + "@b.co";
        assertTrue(email50.length() == 50);
        assertTrue(LoginIdentityUtils.isLoginIdLengthValid(email50));
    }

    @Test
    void emailOverMaxLengthIsInvalid()
    {
        String email51 = "a" + "x".repeat(45) + "@b.co";
        assertTrue(email51.length() == 51);
        assertFalse(LoginIdentityUtils.isLoginIdLengthValid(email51));
    }

    @Test
    void usernameAtMaxLengthIsValid()
    {
        assertTrue(LoginIdentityUtils.isLoginIdLengthValid("abcdefghij1234567890"));
    }

    @Test
    void usernameOverMaxLengthIsInvalid()
    {
        assertFalse(LoginIdentityUtils.isLoginIdLengthValid("abcdefghij12345678901"));
    }

    @Test
    void emptyIsInvalid()
    {
        assertFalse(LoginIdentityUtils.isLoginIdLengthValid(""));
        assertFalse(LoginIdentityUtils.isLoginIdLengthValid(null));
    }
}
