import { Navbar, NavbarBrand} from "@heroui/react";

export default function TitleBar(){
	return(
    <Navbar position="static">
      <NavbarBrand>
        <p className="font-bold text-inherit">GreenBit</p>
      </NavbarBrand>
    </Navbar>
	)
}
