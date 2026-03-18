import { SVGProps, JSX } from "react";
import { Button, Input } from "@heroui/react";
import { useNavigate } from "react-router-dom";

export const MailIcon = (props: SVGProps<SVGSVGElement>) => {
	return (
		<svg aria-hidden="true" fill="none" focusable="false" height="1em" role="presentation" viewBox="0 0 24 24" width="1em" {...props}>
			<path d="M17 3.5H7C4 3.5 2 5 2 8.5V15.5C2 19 4 20.5 7 20.5H17C20 20.5 22 19 22 15.5V8.5C22 5 20 3.5 17 3.5ZM17.47 9.59L14.34 12.09C13.68 12.62 12.84 12.88 12 12.88C11.16 12.88 10.31 12.62 9.66 12.09L6.53 9.59C6.21 9.33 6.16 8.85 6.41 8.53C6.67 8.21 7.14 8.15 7.46 8.41L10.59 10.91C11.35 11.52 12.64 11.52 13.4 10.91L16.53 8.41C16.85 8.15 17.33 8.2 17.58 8.53C17.84 8.85 17.79 9.33 17.47 9.59Z" fill="currentColor" />
		</svg>
	);
};

export default function LoginPage(): JSX.Element {
	const navigate = useNavigate();
	async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
		e.preventDefault();
		try {
			const formData = new FormData(e.currentTarget);
			const API_URL = import.meta.env.VITE_API_URL;
			const mail = formData.get("Email") as string;
			const pass = formData.get("Password") as string;

			// 1. Prepare Form-URLEncoded data (Required by OAuth2PasswordRequestForm)
			const loginData = new URLSearchParams();
			loginData.append("username", mail); // 🚨 MUST be "username" for FastAPI backend
			loginData.append("password", pass);

			const res = await fetch(`${API_URL}/login`, {
				method: "POST",
				headers: {
					"Content-Type": "application/x-www-form-urlencoded", // 🚨 Correct Header
				},
				body: loginData,
			});

			if (res.ok) {
				const data = await res.json(); // 🚨 Access token is in the JSON body
				if (data.access_token) {
					localStorage.setItem("token", data.access_token);
					console.log("Login successful!");
					navigate("/home");
				} else {
					console.log("Token missing in response");
				}
			} else {
				console.log("Wrong Password or Email");
			}
		} catch (err) {
			console.log(`Error while logging in: ${err}`);
		}
	}

	return (
		<div className="w-screen h-screen flex flex-col justify-center items-center">
			<form className="w-[50vw] max-w-[500px] flex flex-col gap-4 items-center justify-center" onSubmit={onSubmit}>
				<Input
					name="Email"
					className="w-full"
					label="Email"
					labelPlacement="outside"
					placeholder="you@example.com"
					startContent={<MailIcon className="text-2xl text-default-400 pointer-events-none shrink-0" />}
					type="email"
					required
				/>
				<Input
					name="Password"
					className="w-full"
					label="Password"
					labelPlacement="outside"
					type="password"
					placeholder="Enter your password"
					required
				/>
				<Button color="primary" type="submit" className="w-full mt-2">
					Submit
				</Button>
			</form>
		</div>
	);
}
