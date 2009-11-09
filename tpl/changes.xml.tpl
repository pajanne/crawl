<response>
    <results name="$response.name" taxonID="$response.taxonID" since="$response.since" count="$response.count" >
    <!-- returns all the detected changes for a particular organism from a certain date  -->
    #for $result in $response.results:
        <gene 
            id="$result.id"
            uniquename="$result.uniquename"
            type="$result.type"
            timelastmodified="$result.timelastmodified"
            rootID="$result.rootid"
            rootUniquename="$result.rootname"
            rootType="$result.roottype"
            />
    #end for
    </results>
</response>