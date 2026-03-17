import {Card, CardBody, CardHeader , CardFooter} from "@heroui/react";
import { Plot } from "./PlotsList.tsx";
export function ListItem(props:Plot){
	return(
    <Card className=" by-10 w-full ">
	<CardHeader>
	Plot Name:{props.plot_name}
	</CardHeader>
      <CardBody>

	  <ul>
	  <li>State:{props.state}</li>
	  <li>Crop:{props.crop}</li>
	  <li>Size(in hectares):{props.size_ha}</li>
	  <li>Annual RainFall:{props.annual_rainfall}</li>
	  </ul>
      </CardBody>
    </Card>
	)
}
