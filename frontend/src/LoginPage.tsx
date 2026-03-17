import { SVGProps , JSX } from "react";
import {Button, Input} from "@heroui/react";
export const MailIcon = (props:SVGProps<SVGSVGElement>) => {
	return (
		<svg
		aria-hidden="true"
		fill="none"
		focusable="false"
		height="1em"
		role="presentation"
		viewBox="0 0 24 24"
		width="1em"
		{...props}
		>
		<path
		d="M17 3.5H7C4 3.5 2 5 2 8.5V15.5C2 19 4 20.5 7 20.5H17C20 20.5 22 19 22 15.5V8.5C22 5 20 3.5 17 3.5ZM17.47 9.59L14.34 12.09C13.68 12.62 12.84 12.88 12 12.88C11.16 12.88 10.31 12.62 9.66 12.09L6.53 9.59C6.21 9.33 6.16 8.85 6.41 8.53C6.67 8.21 7.14 8.15 7.46 8.41L10.59 10.91C11.35 11.52 12.64 11.52 13.4 10.91L16.53 8.41C16.85 8.15 17.33 8.2 17.58 8.53C17.84 8.85 17.79 9.33 17.47 9.59Z"
		fill="currentColor"
		/>
		</svg>
	);
};

export default function LoginPage():JSX.Element{
	async function onSubmit( e: React.FormEvent<HTMLFormElement>){
		e.preventDefault();
		try{
			const formData=new FormData(e.currentTarget);
			const API_URL = import.meta.env.VITE_API_URL;
			const mail=formData.get("Email");
			const pass=formData.get("Password");
			const res=await fetch(`${API_URL}/api/login`,
								  {
									method:"POST",
									headers:{
										"Content-Type": "application/json",
									},
									body: JSON.stringify({
										email:mail ,
										password:pass 
									}),
								}
							 );
			if(res.ok){
				const token :string|null = res.headers.get("token");
				if(token){
					localStorage.setItem("token", token );
				}else{
					console.log("There is some issue while logging in");
				}
			}else{
				console.log("Wrong Password or Username");
			}
		}catch(err){
			console.log(`error while logging in: ${err}`);
		}

	}
	return(
		<div className="w-screen h-screen flex flex-col justify-center items-center">
			<form className="w-[50vw] max-w-[500px] flex flex-col items-center justify-center " onSubmit={onSubmit}>
				{/*email textbox*/}
				<Input
				name="Email"
				className=" py-2 w-full "
				label="Email"
				labelPlacement="outside"
				placeholder="you@example.com"
				startContent={
					<MailIcon className="text-2xl text-default-400 pointer-events-none shrink-0" />
				}
				type="email"
				/>
				{/*password textbox*/}
				<Input
				name="Password"
				className=" py-2 w-full "
				label="Password"
				labelPlacement="outside"
				type="password"
				placeholder="Enter your password"
				/>

				{/*submit button*/}
				<Button color="primary" type="submit" className="py-2 w-full " >
				Submit
				</Button>
			</form>
		</div>
	)
}
