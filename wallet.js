import { BrowserProvider } from "ethers";
import { api } from "./api";

export async function signInWithEthereum() {
  if (!window.ethereum) {
    throw new Error("No wallet found. Install MetaMask or another injected wallet extension.");
  }
  const provider = new BrowserProvider(window.ethereum);
  const signer = await provider.getSigner();
  const address = await signer.getAddress();

  const { message } = await api.getNonce(address);
  const signature = await signer.signMessage(message);
  const { access_token } = await api.verify(address, message, signature);

  return { address, token: access_token };
}
