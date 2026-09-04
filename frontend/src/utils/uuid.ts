/**
 * Generates a RFC4122 v4 compliant UUID string.
 * Uses native `crypto.randomUUID()` in secure contexts (HTTPS) and fallbacks
 * to `crypto.getRandomValues()` when randomUUID is unavailable in HTTP contexts.
 */
export function generateUUID(): string {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID();
  }

  // Secure RFC4122 v4 fallback using getRandomValues
  if (typeof crypto !== 'undefined' && typeof crypto.getRandomValues === 'function') {
    const bytes = new Uint8Array(16);
    crypto.getRandomValues(bytes);
    
    // Set RFC4122 version to 4 (0100)
    bytes[6] = (bytes[6] & 0x0f) | 0x40;
    // Set RFC4122 variant to 10xx
    bytes[8] = (bytes[8] & 0x3f) | 0x80;

    const hex = Array.from(bytes, (byte) => byte.toString(16).padStart(2, '0')).join('');
    return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
  }

  // Final fallback
  return '10000000-1000-4000-8000-100000000000'.replace(/[018]/g, (c) => {
    const num = parseInt(c, 10);
    return (num ^ (Math.floor(Math.random() * 16) >> (num / 4))).toString(16);
  });
}
