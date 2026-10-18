import { base64UrlToBytes, bytesToBase64Url, utf8Bytes } from "./codec.js";
import { VISUAL_LIMITS } from "./limits.js";
const encoder = new TextEncoder();
const decoder = new TextDecoder();
export function encodeStateFragment(state, presentation = {}) {
    const params = new URLSearchParams();
    params.set("v", "1");
    params.set("s", bytesToBase64Url(state));
    if (Object.keys(presentation).length) {
        params.set("p", bytesToBase64Url(encoder.encode(JSON.stringify(presentation))));
    }
    const fragment = params.toString();
    if (utf8Bytes(fragment) > VISUAL_LIMITS.stateUrlBytes) {
        throw new Error("state is too large for a shareable URL; export a state file instead");
    }
    return fragment;
}
export function decodeStateFragment(hash) {
    const raw = hash.startsWith("#") ? hash.slice(1) : hash;
    if (!raw)
        return null;
    if (utf8Bytes(raw) > VISUAL_LIMITS.stateUrlBytes)
        throw new Error("state URL exceeds supported size");
    const params = new URLSearchParams(raw);
    if (params.get("v") !== "1")
        throw new Error("unsupported state URL version");
    const encodedState = params.get("s");
    if (!encodedState)
        throw new Error("state URL is missing candidate state");
    let presentation = {};
    const encodedPresentation = params.get("p");
    if (encodedPresentation) {
        const parsed = JSON.parse(decoder.decode(base64UrlToBytes(encodedPresentation)));
        if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
            throw new Error("invalid presentation state");
        }
        const borders = parsed.borders;
        if (borders !== undefined && typeof borders !== "boolean") {
            throw new Error("presentation borders must be boolean");
        }
        presentation = borders === undefined ? {} : { borders };
    }
    return { state: base64UrlToBytes(encodedState), presentation };
}
