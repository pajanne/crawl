<response>
    <results name=$response.name>
    #for $service in $response.services:
    <service name=$service />
    #end for
    </results>
</response>
