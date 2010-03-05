<response>
    <results name="$response.name" taxonomyID="$response.taxonomyID" since="$response.since"  count="$response.count" >
    <!-- returns a list of manual annotations of biologically relevant changes stored in a private field at the polypeptide level -->
    #for $result in $response.results:
        <gene 
            geneuniquename="$result.geneuniquename" 
            mrnauniquename="$result.mrnauniquename" 
            transcriptuniquename="$result.transcriptuniquename"
            date="$result.changedate"
            change="$result.changedetail"
            source="$result.source"
            />
    #end for
    </results>
</response>