// Locks a home code in the browser so it can sit in the public homes.txt file.
// Only the private key (GitHub secret HOMES_KEY) can unlock it: alert.py _unlock().
// Format: "olf1:" + base64url( RSA-OAEP-SHA256(aes key) [256 B] | iv [12 B] | AES-GCM(json) ).
const OLF_PUBKEY = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAoV5IP/xTA2ok1HMLBPqX6AVVO3oZIVBjKuXXkvIjhg/lxAiQI3sJKllhxoJITLV9CwmCK/ZW57RJeKYYXc7jwuAlxa1AVtJDwwFnWSsR2OA1jtPGiqhXQF22zg0fdnd0Lt0YXvguE/6aWfptuCQpw0TkRb6FwPLdjDcDkbaPQXIVVuKG5IG/ZmhV7Fr92Yo3GXszgxnD6Hf3btWrOOHAGJtH44ktsed1WY34pKpZBqRD4CMcd6fS3Gqtp/H/vpV9abHGLkBsUxgyqT7F0n1Oq7UcVbUym64hNwpRlJKKCpDLDB/WxoaLBAETqbgvL0iTGkDgYSJcdxUXZj8tSnh4awIDAQAB";

async function olfLock(obj) {
  const b = (s) => Uint8Array.from(atob(s), (c) => c.charCodeAt(0));
  const pub = await crypto.subtle.importKey("spki", b(OLF_PUBKEY), { name: "RSA-OAEP", hash: "SHA-256" }, false, ["encrypt"]);
  const aes = await crypto.subtle.generateKey({ name: "AES-GCM", length: 256 }, true, ["encrypt"]);
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const wrapped = new Uint8Array(await crypto.subtle.encrypt({ name: "RSA-OAEP" }, pub, await crypto.subtle.exportKey("raw", aes)));
  const body = new Uint8Array(await crypto.subtle.encrypt({ name: "AES-GCM", iv }, aes, new TextEncoder().encode(JSON.stringify(obj))));
  const all = new Uint8Array(wrapped.length + iv.length + body.length);
  all.set(wrapped); all.set(iv, wrapped.length); all.set(body, wrapped.length + iv.length);
  let s = ""; all.forEach((x) => { s += String.fromCharCode(x); });
  return "olf1:" + btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
