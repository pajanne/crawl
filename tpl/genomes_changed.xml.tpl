<response>
    <results name=$response.name since=$response.since >
    <!-- returns all the organisms in the database and summary count of all the detected changes from a certain date -->
    #for $result in $response.results:
        <organism 
            name=$result.name
            id=$result.organism_id
            taxonomyID=$result.taxonomyid
            count=$result.count
            />
    #end for
    </results>
</response>