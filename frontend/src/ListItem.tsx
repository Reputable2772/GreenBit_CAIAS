import {Card, CardBody, CardHeader , CardFooter} from "@heroui/react";
import { Plot } from "./PlotsList.tsx";
import { Link } from "react-router-dom";

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
	  <CardFooter>
	  <Link to={`/plots/${props.id}`} className="text-blue-500">
	  View Details →
	  </Link>
	  </CardFooter>
    </Card>
	)
}
