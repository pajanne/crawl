<response>
    <results name="$response.name" uniqueName="$response.uniqueName" >
    <!-- returns the locations of features located on a source feature  -->
    #for $feature in $response.features:
        <gene 
            uniqueName="$feature.uniquename"
            seqlen="$feature.seqlen"
            fstart="$feature.fstart"
            fend="$feature.fend"
            phase="$feature.phase"
            strand="$feature.strand"
            score="$feature.score"
            type="$feature.type"
            />
    #end for
    </results>
</response>