from pathlib import Path

from lxml import etree

from process_running_state.bpmn_model import BPMNModel, BPMNNodeType
from process_running_state.petri_net import PetriNet


def read_bpmn_model(model_path: Path) -> BPMNModel:
    try:
        # Parse the XML file
        tree = etree.parse(model_path)
        root = tree.getroot()
        # Define the namespace map for BPMN
        ns = {'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL'}
        # Find all process elements using XPath with namespaces
        processes = root.xpath('.//bpmn:process', namespaces=ns)
        if len(processes) > 1:
            print("Warning! Reading BPMN file with more than one process defined. Parsing first match.")
        bpmn_model = BPMNModel()
        process = processes[0]
        # Process attributes
        # process_id = process.get('id')
        # process_name = process.get('name', 'Unnamed Process')
        # Processing tasks
        tasks = process.xpath('.//bpmn:task', namespaces=ns)
        for task in tasks:
            task_id = task.get("id")
            task_name = task.get("name", task_id)
            bpmn_model.add_task(task_id, task_name)
        # Processing start events
        start_events = process.xpath(".//bpmn:startEvent", namespaces=ns)
        for event in start_events:
            event_id = event.get("id")
            event_name = event.get("name", event_id)
            bpmn_model.add_event(event_type=BPMNNodeType.START_EVENT, event_id=event_id, event_name=event_name)
        # Processing end events
        end_events = process.xpath(".//bpmn:endEvent", namespaces=ns)
        for event in end_events:
            event_id = event.get("id")
            event_name = event.get("name", event_id)
            bpmn_model.add_event(event_type=BPMNNodeType.END_EVENT, event_id=event_id, event_name=event_name)
        # Processing intermediate events
        inter_events = process.xpath('.//bpmn:intermediateThrowEvent | .//bpmn:intermediateCatchEvent', namespaces=ns)
        for event in inter_events:
            event_id = event.get("id")
            event_name = event.get("name", event_id)
            bpmn_model.add_event(event_type=BPMNNodeType.INTERMEDIATE_EVENT, event_id=event_id, event_name=event_name)
        # Processing AND gateways
        and_gateways = process.xpath('.//bpmn:parallelGateway', namespaces=ns)
        for gateway in and_gateways:
            gateway_id = gateway.get("id")
            gateway_name = gateway.get("name", gateway_id)
            bpmn_model.add_gateway(BPMNNodeType.PARALLEL_GATEWAY, gateway_id, gateway_name)
        # Processing XOR gateways
        xor_gateways = process.xpath('.//bpmn:exclusiveGateway', namespaces=ns)
        for gateway in xor_gateways:
            gateway_id = gateway.get("id")
            gateway_name = gateway.get("name", gateway_id)
            bpmn_model.add_gateway(BPMNNodeType.EXCLUSIVE_GATEWAY, gateway_id, gateway_name)
        # Processing OR gateways
        or_gateways = process.xpath('.//bpmn:inclusiveGateway', namespaces=ns)
        for gateway in or_gateways:
            gateway_id = gateway.get("id")
            gateway_name = gateway.get("name", gateway_id)
            bpmn_model.add_gateway(BPMNNodeType.INCLUSIVE_GATEWAY, gateway_id, gateway_name)
        # Processing flows
        flows = process.xpath('.//bpmn:sequenceFlow', namespaces=ns)
        for flow in flows:
            flow_id = flow.get("id")
            flow_name = flow.get("name", flow_id)
            source_id = flow.get("sourceRef")
            target_id = flow.get("targetRef")
            bpmn_model.add_flow(flow_id, flow_name, source_id, target_id)
        # Return build BPMN model
        return bpmn_model
    except etree.XMLSyntaxError as e:
        print(f"XML Syntax Error: {e}")


def read_petri_net(model_path: Path) -> PetriNet:
    try:
        # Load and parse the XML file
        tree = etree.parse(model_path)
        root = tree.getroot()
        ns = {'pnml': "http://www.pnml.org/version-2009/grammar/pnmlcoremodel"}
        # Build Petri net
        petri_net = PetriNet()
        # Parse places
        for place in root.findall("net/page/place", namespaces=ns):
            place_id = place.get("id")
            place_name = place.find("name/text", namespaces=ns)
            petri_net.add_place(
                place_id=place_id,
                place_name=place_name.text if place_name is not None else place_id
            )
        # Parse transitions
        for transition in root.findall("net/page/transition", namespaces=ns):
            transition_id = transition.get("id")
            transition_name = transition.find("name/text", namespaces=ns)
            toolspecific = transition.find("toolspecific", namespaces=ns)
            is_silent = toolspecific is not None and toolspecific.get("activity") == "$invisible$"
            petri_net.add_transition(
                transition_id=transition_id,
                transition_name=transition_name.text if transition_name is not None else transition_id,
                invisible=is_silent
            )
        # Parse edges
        for edge in root.findall("net/page/arc", namespaces=ns):
            source = edge.get("source")
            target = edge.get("target")
            petri_net.add_edge(source_id=source, target_id=target)
        # Initial marking
        petri_net.initial_marking = set()
        for place in root.findall("net/page/place", namespaces=ns):
            if place.find("initialMarking", namespaces=ns):
                if int(place.find("initialMarking/text", namespaces=ns).text) > 0:
                    petri_net.initial_marking |= {place.get("id")}
        # Final marking
        petri_net.final_markings = []
        for marking in root.findall("net/finalmarkings/marking", namespaces=ns):
            new_marking = set()
            for place in marking.findall("place", namespaces=ns):
                if int(place.find("text", namespaces=ns).text) > 0:
                    new_marking |= {place.get("idref")}
            petri_net.final_markings += [new_marking]
        # Return Petri net
        return petri_net
    except etree.XMLSyntaxError as e:
        print(f"XML Syntax Error: {e}")
